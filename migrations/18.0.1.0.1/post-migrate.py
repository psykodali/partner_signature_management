def migrate(cr, version):
    """
    Post-migration script to compute new field values
    """
    # This runs AFTER the module upgrade and schema changes
    # Force recomputation of all new fields
    from odoo import registry, SUPERUSER_ID
    
    reg = registry(cr.dbname)
    with reg.cursor() as new_cr:
        env = reg['ir.model.data'].browse(new_cr, SUPERUSER_ID, []).env
        
        # Recompute all partner fields
        partners = env['res.partner'].search([])
        if partners:
            partners._compute_own_signature_transaction_count()
            partners._compute_own_signature_transaction_count_this_year()
            partners._compute_own_paid_transactions_this_year()
            partners._compute_own_pending_transactions()
            partners._compute_pending_transactions()
            partners._compute_forecast_transaction_price()
