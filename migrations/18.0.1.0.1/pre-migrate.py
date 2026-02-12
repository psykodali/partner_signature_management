def migrate(cr, version):
    """
    Pre-migration script to create database columns before module loads
    """
    # Create columns if they don't exist yet
    # This prevents the "column does not exist" error during server startup
    
    # Check if pending_transactions column exists
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='res_partner' AND column_name='pending_transactions'
    """)
    if not cr.fetchone():
        cr.execute("""
            ALTER TABLE res_partner 
            ADD COLUMN pending_transactions INTEGER DEFAULT 0
        """)
    
    # Check if forecast_transaction_price column exists
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='res_partner' AND column_name='forecast_transaction_price'
    """)
    if not cr.fetchone():
        cr.execute("""
            ALTER TABLE res_partner 
            ADD COLUMN forecast_transaction_price NUMERIC(10,4) DEFAULT 0.0
        """)

