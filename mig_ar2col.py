#! /usr/bin/python3
# -*- coding: utf-8 -*-
from arb_xmlrpc_migration import odoo_xmlrpc_migration

origin_company_id = 4

plan = odoo_xmlrpc_migration(
    '/opt/scripts/arbusta/odoo_xmlrcp_migration_ar2col.conf')

plan.modules.append('account')
plan.modules.append('product')
mig = True


plan.context = {
            'check_move_validity': False,
            'default_type': 'out_invoice'
}   

if mig:

    move_ids = plan.search('account.move', [
        ('company_id', '=', origin_company_id),
        ('state', '=', 'draft'),
        ('type', '=', 'out_invoice'),
        ('x_studio_field_PZO8w', '=', True)

    ]
    )
    res = plan.migrate('account.move', domain=[
        ('id', 'in', move_ids)
        ]
    )
    res = plan.migrate('account.move.line', 
        domain=[('move_id', 'in', move_ids), ('exclude_from_invoice_tab', '=', False)]
    )
    draft_moves = plan.search('account.move', [('state', '=', 'draft'), ('type', '=', 'out_invoice')], 'to')
    plan.execute_method_chunked('account.move', 'post', draft_moves, 'to')
    plan.execute_method_chunked('account.move', 'post', move_ids, 'from')
