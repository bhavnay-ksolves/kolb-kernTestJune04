# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError
from datetime import datetime
import base64

class RiskReportWizard(models.TransientModel):
    _name = 'risk.report.wizard'
    _description = 'Risk Report Wizard'


    def action_report(self):
        """
        Generates the risk assessment PDF and sets the report creation date.

        Returns:
            dict: Action to generate and download the risk assessment report.
        """
        project = self.env['project.project'].browse(self.env.context.get('active_id'))
        project.write({'date_report_creation': datetime.now()})
        return self.env.ref(
            'ks_risk_assessment.action_risk_assessment_pdf'
        ).report_action(project)

    def action_send_esignature(self):
        """
        Sends an e-signature request for the risk assessment report.

        Raises:
            UserError: If the customer does not have an email address or the report is not found.

        Returns:
            dict: Action to send the e-signature request.
        """
        self.ensure_one()
        project = self.env['project.project'].browse(self.env.context.get('active_id'))

        # Check that partner has email
        if not project.partner_id or not project.partner_id.email:
            raise UserError("Customer must have an email address to send e-signature request.")

        # Get the report and render PDF
        report = self.env['ir.actions.report']._get_report_from_name(
            'ks_risk_assessment.report_risk_assessment_document')
        if not report:
            raise UserError("Risk report not found.")

        pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
            'ks_risk_assessment.report_risk_assessment_document', project.id
        )

        # Create PDF attachment
        attachment = self.env['ir.attachment'].create({
            'name': f"Risk_Assessment_{project.name or project.id}.pdf",
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': project._name,
            'res_id': project.id,
            'mimetype': 'application/pdf',
        })
        tag = self.env['sign.template.tag'].search([('name', '=', 'Risk Assessment Report')], limit=1)
        # Create new template from attachment
        sign_template = self.env['sign.template'].create({
            'attachment_id': attachment.id,
            'name': f"Risk Assessment Template - {project.name or project.id}",
            'project_id': project.id,
            'tag_ids': [(6, 0, [tag.id])] if tag else [],
        })
        return {
            "type": "ir.actions.client",
            "tag": "sign.Template",
            "name": f"Template {attachment.name}",
            "target": "current",
            "params": {
                "sign_edit_call": "sign_send_request",
                "id": sign_template.id,
                "sign_directly_without_mail": False,
                "resModel": project._name,
            },
        }


