#!/usr/bin/env python3
"""
Odoo MCP Server for Accounting Integration
Implements Model Context Protocol for Odoo Community Edition integration
Supports JSON-RPC APIs for accounting operations
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import xmlrpc.client

from mcp.server import Server
from mcp.types import (
    CallToolResult,
    TextContent,
    Tool,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OdooClient:
    """Odoo JSON-RPC client for accounting operations"""

    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.connected = False

        # Establish connection
        try:
            self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
            self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
            # Authenticate
            self.uid = self.common.authenticate(db, username, password, {})
            if self.uid:
                self.connected = True
                logger.info(f"Successfully connected to Odoo: {url}")
            else:
                logger.warning("Odoo authentication failed - check credentials")
        except Exception as e:
            logger.warning(f"Could not connect to Odoo (server may not be running): {e}")
            self.connected = False

    def search_read(self, model: str, domain: List = None, fields: List[str] = None, offset: int = 0, limit: int = None) -> List[Dict]:
        """Search and read records from Odoo"""
        if not self.connected:
            return []
        if domain is None:
            domain = []
        if fields is None:
            fields = []

        try:
            result = self.models.execute_kw(
                self.db, self.uid, self.password,
                model, 'search_read',
                [domain], {'fields': fields, 'offset': offset, 'limit': limit}
            )
            return result
        except Exception as e:
            logger.error(f"Search read error for model {model}: {e}")
            return []

    def create_record(self, model: str, vals: Dict) -> int:
        """Create a new record in Odoo"""
        if not self.connected:
            return -1
        try:
            result = self.models.execute_kw(
                self.db, self.uid, self.password,
                model, 'create',
                [vals]
            )
            return result
        except Exception as e:
            logger.error(f"Create error for model {model}: {e}")
            return -1

    def update_record(self, model: str, record_id: int, vals: Dict) -> bool:
        """Update an existing record in Odoo"""
        if not self.connected:
            return False
        try:
            result = self.models.execute_kw(
                self.db, self.uid, self.password,
                model, 'write',
                [[record_id], vals]
            )
            return result
        except Exception as e:
            logger.error(f"Update error for model {model} ID {record_id}: {e}")
            return False


# Initialize server
server = Server("odoo-mcp-server")

# Global Odoo client
odoo_client = None


def get_odoo_client() -> OdooClient:
    """Get or create Odoo client"""
    global odoo_client
    if odoo_client is None:
        odoo_url = os.getenv('ODOO_URL', 'http://localhost:8069')
        odoo_db = os.getenv('ODOO_DB', 'odoo_db')
        odoo_username = os.getenv('ODOO_USERNAME', 'admin')
        odoo_password = os.getenv('ODOO_PASSWORD', 'password')
        odoo_client = OdooClient(odoo_url, odoo_db, odoo_username, odoo_password)
    return odoo_client


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available Odoo tools"""
    return [
        Tool(
            name="odoo_get_invoices",
            description="Retrieve invoices from Odoo accounting system",
            inputSchema={
                "type": "object",
                "properties": {
                    "state": {"type": "string", "description": "Filter by invoice state (draft, posted, paid)"},
                    "limit": {"type": "integer", "description": "Maximum number of invoices to return", "default": 20}
                }
            }
        ),
        Tool(
            name="odoo_create_invoice",
            description="Create a new invoice in Odoo accounting system (requires approval)",
            inputSchema={
                "type": "object",
                "properties": {
                    "partner_id": {"type": "integer", "description": "Customer/partner ID"},
                    "invoice_date": {"type": "string", "description": "Invoice date (YYYY-MM-DD)"},
                    "amount_total": {"type": "number", "description": "Total invoice amount"},
                    "lines": {
                        "type": "array",
                        "description": "Invoice line items",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "integer"},
                                "quantity": {"type": "number"},
                                "price_unit": {"type": "number"}
                            }
                        }
                    }
                },
                "required": ["partner_id", "invoice_date", "amount_total"]
            }
        ),
        Tool(
            name="odoo_get_partners",
            description="Retrieve partners/customers from Odoo",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of partners", "default": 20}
                }
            }
        ),
        Tool(
            name="odoo_get_products",
            description="Retrieve products from Odoo",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of products", "default": 20}
                }
            }
        ),
        Tool(
            name="odoo_get_bank_transactions",
            description="Retrieve bank transactions from Odoo",
            inputSchema={
                "type": "object",
                "properties": {
                    "date_from": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "date_to": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                    "limit": {"type": "integer", "description": "Maximum transactions", "default": 50}
                }
            }
        ),
        Tool(
            name="odoo_generate_accounting_summary",
            description="Generate a summary of accounting data for CEO briefing",
            inputSchema={
                "type": "object",
                "properties": {
                    "period_start": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "period_end": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                }
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls to interact with Odoo"""
    client = get_odoo_client()

    if not client.connected:
        return [TextContent(
            type="text",
            text="Note: Odoo server is not connected. Using simulated data for demonstration.\n\n" +
                 _get_simulated_response(name, arguments)
        )]

    try:
        if name == "odoo_get_invoices":
            return await _get_invoices(client, arguments)
        elif name == "odoo_create_invoice":
            return await _create_invoice(client, arguments)
        elif name == "odoo_get_partners":
            return await _get_partners(client, arguments)
        elif name == "odoo_get_products":
            return await _get_products(client, arguments)
        elif name == "odoo_get_bank_transactions":
            return await _get_bank_transactions(client, arguments)
        elif name == "odoo_generate_accounting_summary":
            return await _generate_accounting_summary(client, arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


def _get_simulated_response(name: str, arguments: Dict[str, Any]) -> str:
    """Return simulated data when Odoo is not connected"""
    if name == "odoo_get_invoices":
        return """Simulated Invoices:
- INV/2026/0001 (posted): $1,500.00 USD for Client A on 2026-01-15
- INV/2026/0002 (draft): $2,300.00 USD for Client B on 2026-01-16
- INV/2026/0003 (paid): $850.00 USD for Client C on 2026-01-10"""

    elif name == "odoo_get_partners":
        return """Simulated Partners:
- Client A: clienta@example.com, +1-555-0101
- Client B: clientb@example.com, +1-555-0102
- Client C: clientc@example.com, +1-555-0103"""

    elif name == "odoo_get_products":
        return """Simulated Products:
- Consulting Services: $150.00/hr
- Development Work: $200.00/hr
- Support Package: $500.00/month"""

    elif name == "odoo_generate_accounting_summary":
        return """Accounting Summary (Simulated):
Period: Last 7 days

Revenue: $4,650.00
- Invoices Issued: 3
- Invoices Paid: 1

Expenses: $1,200.00
- Software Subscriptions: $300.00
- Services: $900.00

Net Income: $3,450.00"""

    return "Simulated response for demonstration purposes."


async def _get_invoices(client: OdooClient, args: Dict[str, Any]) -> List[TextContent]:
    """Get invoices from Odoo"""
    domain = []
    if 'state' in args:
        domain.append(('state', '=', args['state']))

    fields = ['id', 'name', 'partner_id', 'amount_total', 'state', 'invoice_date', 'currency_id']
    limit = args.get('limit', 20)

    invoices = client.search_read('account.move', domain, fields, limit=limit)

    if not invoices:
        return [TextContent(type="text", text="No invoices found.")]

    response_text = f"Found {len(invoices)} invoices:\n"
    for inv in invoices:
        partner_name = inv['partner_id'][1] if inv.get('partner_id') else 'Unknown'
        currency_name = inv['currency_id'][1] if inv.get('currency_id') else 'USD'
        response_text += f"- {inv.get('name', 'N/A')} ({inv.get('state', 'N/A')}): {inv.get('amount_total', 0)} {currency_name} for {partner_name}\n"

    return [TextContent(type="text", text=response_text)]


async def _create_invoice(client: OdooClient, args: Dict[str, Any]) -> List[TextContent]:
    """Create an invoice in Odoo"""
    invoice_vals = {
        'move_type': 'out_invoice',
        'partner_id': args['partner_id'],
        'invoice_date': args['invoice_date'],
    }

    line_vals = []
    for line in args.get('lines', []):
        line_vals.append((0, 0, {
            'product_id': line['product_id'],
            'quantity': line['quantity'],
            'price_unit': line['price_unit'],
        }))

    if line_vals:
        invoice_vals['invoice_line_ids'] = line_vals

    invoice_id = client.create_record('account.move', invoice_vals)

    if invoice_id > 0:
        return [TextContent(type="text", text=f"Invoice created successfully with ID: {invoice_id}")]
    else:
        return [TextContent(type="text", text="Failed to create invoice.")]


async def _get_partners(client: OdooClient, args: Dict[str, Any]) -> List[TextContent]:
    """Get partners from Odoo"""
    fields = ['id', 'name', 'email', 'phone', 'street', 'city']
    limit = args.get('limit', 20)

    partners = client.search_read('res.partner', [], fields, limit=limit)

    if not partners:
        return [TextContent(type="text", text="No partners found.")]

    response_text = f"Found {len(partners)} partners:\n"
    for p in partners:
        response_text += f"- {p.get('name', 'N/A')}: {p.get('email', 'N/A')}, {p.get('phone', 'N/A')}\n"

    return [TextContent(type="text", text=response_text)]


async def _get_products(client: OdooClient, args: Dict[str, Any]) -> List[TextContent]:
    """Get products from Odoo"""
    fields = ['id', 'name', 'list_price', 'standard_price', 'categ_id']
    limit = args.get('limit', 20)

    products = client.search_read('product.product', [], fields, limit=limit)

    if not products:
        return [TextContent(type="text", text="No products found.")]

    response_text = f"Found {len(products)} products:\n"
    for p in products:
        category = p['categ_id'][1] if p.get('categ_id') else 'Uncategorized'
        response_text += f"- {p.get('name', 'N/A')}: ${p.get('list_price', 0)} (cost: ${p.get('standard_price', 0)}) [{category}]\n"

    return [TextContent(type="text", text=response_text)]


async def _get_bank_transactions(client: OdooClient, args: Dict[str, Any]) -> List[TextContent]:
    """Get bank transactions from Odoo"""
    domain = []
    if 'date_from' in args:
        domain.append(('date', '>=', args['date_from']))
    if 'date_to' in args:
        domain.append(('date', '<=', args['date_to']))

    fields = ['id', 'name', 'amount', 'date', 'partner_id', 'ref']
    limit = args.get('limit', 50)

    transactions = client.search_read('account.bank.statement.line', domain, fields, limit=limit)

    if not transactions:
        return [TextContent(type="text", text="No bank transactions found for the specified period.")]

    response_text = f"Found {len(transactions)} transactions:\n"
    for t in transactions:
        partner = t['partner_id'][1] if t.get('partner_id') else 'Unknown'
        response_text += f"- {t.get('date', 'N/A')}: ${t.get('amount', 0)} - {t.get('ref', 'N/A')} ({partner})\n"

    return [TextContent(type="text", text=response_text)]


async def _generate_accounting_summary(client: OdooClient, args: Dict[str, Any]) -> List[TextContent]:
    """Generate accounting summary for CEO briefing"""
    period_start = args.get('period_start', (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))
    period_end = args.get('period_end', datetime.now().strftime('%Y-%m-%d'))

    # Get invoices for the period
    invoice_domain = [
        ('invoice_date', '>=', period_start),
        ('invoice_date', '<=', period_end),
        ('move_type', 'in', ['out_invoice', 'out_refund'])
    ]
    invoices = client.search_read('account.move', invoice_domain,
                                   ['amount_total', 'state', 'payment_state'], limit=100)

    total_revenue = sum(inv.get('amount_total', 0) for inv in invoices)
    invoices_issued = len(invoices)
    invoices_paid = len([inv for inv in invoices if inv.get('payment_state') == 'paid'])

    # Get expenses (vendor bills)
    expense_domain = [
        ('invoice_date', '>=', period_start),
        ('invoice_date', '<=', period_end),
        ('move_type', 'in', ['in_invoice', 'in_refund'])
    ]
    expenses = client.search_read('account.move', expense_domain, ['amount_total'], limit=100)
    total_expenses = sum(exp.get('amount_total', 0) for exp in expenses)

    net_income = total_revenue - total_expenses

    summary = f"""
# Accounting Summary
**Period:** {period_start} to {period_end}

## Revenue
- **Total Revenue:** ${total_revenue:,.2f}
- **Invoices Issued:** {invoices_issued}
- **Invoices Paid:** {invoices_paid}

## Expenses
- **Total Expenses:** ${total_expenses:,.2f}

## Net Income
- **Net Income:** ${net_income:,.2f}

---
*Generated by Odoo MCP Server*
"""

    return [TextContent(type="text", text=summary)]


async def main():
    """Run the MCP server"""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
