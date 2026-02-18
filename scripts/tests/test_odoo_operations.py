import os
import xmlrpc.client
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

url = os.getenv("ODOO_URL")
db = os.getenv("ODOO_DB")
username = os.getenv("ODOO_USERNAME")
password = os.getenv("ODOO_PASSWORD")

print(f"🔌 Connecting to {url}...")

try:
    # 1. Authenticate
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        print("❌ Authentication Failed.")
        exit()
        
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    print(f"✅ Authenticated (UID: {uid})")

    # 2. Create a Test Partner (Customer)
    print("\n👤 Creating Test Customer...")
    partner_vals = {
        'name': 'AI Employee Test Partner',
        'email': 'ai_test@example.com',
        'phone': '123-456-7890',
    }
    partner_id = models.execute_kw(db, uid, password, 'res.partner', 'create', [partner_vals])
    print(f"✅ Created Partner ID: {partner_id}")

    # 3. Create a Draft Invoice
    print("\n💰 Creating Draft Invoice...")
    invoice_vals = {
        'move_type': 'out_invoice',  # Customer Invoice
        'partner_id': partner_id,
        'invoice_date': time.strftime('%Y-%m-%d'),
        'invoice_line_ids': [
            (0, 0, {
                'name': 'AI Optimization Service',
                'quantity': 1,
                'price_unit': 500.0,
            }),
            (0, 0, {
                'name': 'Server Maintenance',
                'quantity': 2,
                'price_unit': 150.0,
            }),
        ],
    }
    invoice_id = models.execute_kw(db, uid, password, 'account.move', 'create', [invoice_vals])
    print(f"✅ Created Invoice ID: {invoice_id}")

    # 4. Read it back
    print("\n🔍 Verifying Data...")
    invoice = models.execute_kw(db, uid, password, 'account.move', 'read', [invoice_id], {'fields': ['name', 'amount_total', 'state']})
    print(f"Invoice Data: {invoice[0]}")

    print("\n✨ SUCCESS! The AI Employee can Read & Write to your Odoo.")
    print("👉 Go to your Odoo Dashboard -> Accounting -> Customers -> Invoices to see the new 'Draft' invoice.")

except Exception as e:
    print(f"❌ Error: {e}")
