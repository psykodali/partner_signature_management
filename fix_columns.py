#!/usr/bin/env python3
"""
Script to manually create database columns for partner_signature_management module.
Run this with: odoo-bin shell -d YOUR_DATABASE_NAME --addons-path=/path/to/addons < fix_columns.py

Or run interactively:
odoo-bin shell -d YOUR_DATABASE_NAME
Then paste the code below.
"""

# Check if pending_transactions column exists
env.cr.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name='res_partner' AND column_name='pending_transactions'
""")
if not env.cr.fetchone():
    print("Creating pending_transactions column...")
    env.cr.execute("""
        ALTER TABLE res_partner 
        ADD COLUMN pending_transactions INTEGER DEFAULT 0
    """)
    env.cr.commit()
    print("✓ pending_transactions column created")
else:
    print("✓ pending_transactions column already exists")

# Check if forecast_transaction_price column exists
env.cr.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name='res_partner' AND column_name='forecast_transaction_price'
""")
if not env.cr.fetchone():
    print("Creating forecast_transaction_price column...")
    env.cr.execute("""
        ALTER TABLE res_partner 
        ADD COLUMN forecast_transaction_price NUMERIC(10,4) DEFAULT 0.0
    """)
    env.cr.commit()
    print("✓ forecast_transaction_price column created")
else:
    print("✓ forecast_transaction_price column already exists")

print("\n✅ All columns created successfully!")
print("Next steps:")
print("1. Exit this shell")
print("2. Edit models/res_partner.py and change store=False to store=True for both fields")
print("3. Restart Odoo server")
print("4. Upgrade the partner_signature_management module")
