def migrate(cr, version):
    """
    Pre-migration script to prepare for new fields
    """
    # This runs BEFORE the module upgrade
    # Odoo will automatically create the new columns during upgrade
    pass
