import os
import xmlrpc.client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

url = os.getenv("ODOO_URL")
db = os.getenv("ODOO_DB")
username = os.getenv("ODOO_USERNAME")
password = os.getenv("ODOO_PASSWORD")

print(f"Connecting to Odoo...")
print(f"URL: {url}")
print(f"DB: {db}")
print(f"User: {username}")

try:
    # 1. Authenticate
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    version = common.version()
    print(f"Odoo Version: {version['server_version']}")
    
    uid = common.authenticate(db, username, password, {})
    
    if uid:
        print(f"✅ Authentication Successful! UID: {uid}")
        
        # 2. Check Models
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # Try to read partners (customers)
        partners = models.execute_kw(db, uid, password,
            'res.partner', 'search_count',
            [[]])
        print(f"✅ Access to Partners verified. Total Partners: {partners}")
        
        # Try to read invoices (account.move)
        invoices = models.execute_kw(db, uid, password,
            'account.move', 'search_count',
            [[]])
        print(f"✅ Access to Accounting verified. Total Invoices/Moves: {invoices}")
        
    else:
        print("❌ Authentication Failed: Invalid credentials.")

except Exception as e:
    print(f"❌ Connection Error: {e}")
