# -*- coding: utf-8 -*-
from odoo import models, fields, api

class DailyConstructionCommentWizard(models.TransientModel):
    _name = 'daily.construction.comment.wizard'
    _description = 'Approval or Rejection Comment Wizard'

    comment = fields.Text(string="Comment", required=True)
    action_type = fields.Selection([
        ('approve', 'Approve'),
        ('reject', 'Reject')
    ], string="Action", required=True)
    report_id = fields.Many2one('daily.construction.report', string="Daily Report")

    def apply_action(self):
        """
            Applies the selected action (approve or reject) to the report.
            Posts a comment in the chatter with the selected action and user comment.
        """
        if self.report_id:
            self.report_id.approval_comment = self.comment
            # Post comment to chatter
            action_label_map = {
                'approve': 'Approved',
                'reject': 'Rejected',
            }
            action_label = action_label_map.get(self.action_type, 'Action')
            self.report_id.message_post(
                body=f"{action_label} :{self.comment}",
                message_type='comment',
                subtype_id=False
            )
            if self.action_type == 'approve':
                self.report_id.action_approve()
            elif self.action_type == 'reject':
                self.report_id.action_reject()
