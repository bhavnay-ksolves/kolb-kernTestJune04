# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.


def migrate(cr, version):
    if not version:
        return

    # Required for odoo.sh migration
    try:
        cr.execute(
            'DELETE FROM ir_ui_view '
            "WHERE arch_db->>'en_US' "
            "ilike '%partner_account_generate_multi_company%';"
        )
    except Exception:  # nosec
        pass

    try:
        cr.execute(
            'DELETE FROM ir_ui_view '
            "WHERE arch_db->>'en_US' "
            "ilike '%property_account_receivable_is_default%';"
        )
    except Exception:  # nosec
        pass
