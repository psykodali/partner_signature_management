def migrate(cr, version):
    """
    Post-migration script to compute new field values
    """
    # This runs AFTER the module upgrade and schema changes
    # Force recomputation of all new fields
    from odoo import registry, SUPERUSER_ID
    
    from odoo import api, SUPERUSER_ID
    
    reg = registry(cr.dbname)
    with reg.cursor() as new_cr:
        env = api.Environment(new_cr, SUPERUSER_ID, {})
        
        # Recompute all partner fields if they exist
        Partner = env['res.partner']
        fields_to_compute = [
            'own_signature_transaction_count',
            'own_signature_transaction_count_this_year',
            'own_paid_transactions_this_year',
            'own_pending_transactions',
            'pending_transactions',
            'forecast_transaction_price'
        ]
        
        # Filter only fields that actually exist in the model
        valid_fields = [f for f in fields_to_compute if f in Partner._fields]
        
        if valid_fields:
            partners = Partner.search([])
            if partners:
                for field in valid_fields:
                    Partner._recompute_recordset(partners._fields[field])
