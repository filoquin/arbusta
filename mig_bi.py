#! /usr/bin/python3
# -*- coding: utf-8 -*-
from arb_xmlrpc_migration import odoo_xmlrpc_migration

origin_company_id = 4

# Genero la interface de conexion de Colombia a Global
col2ar = odoo_xmlrpc_migration(
    '/opt/scripts/arbusta/odoo_xmlrcp_migration_col2ar.conf')
col2ar.modules.append('account')
col2ar.modules.append('product')
col2ar.modules.append('analytic')


# Configuraciones de test
mig = True
col2ar.chunk_size = 20
col2ar.is_test = True
col2ar.chunk_size = 100
col2ar.is_test = False


# Obtengo los ids que necesito para busquedas y valores por defecto
it_fid = col2ar.get_external_id('l10n_latam.identification.type', 'it_fid', 'to')[0]['res_id']
inv_journal = col2ar.search('account.journal', [('code', '=', 'INV')])[0]

# defino los contextos para la creacion de info 
col2ar.context = {
    'check_move_validity': False,
    'default_type': 'out_invoice',
    'default_company_id': origin_company_id,
    'default_l10n_latam_identification_type_id': it_fid
}
if mig:
    #col2ar.migrate('res.partner', domain=[('fe_nit', '!=', False), ('fe_nit', '!=', '')])

    move_ids = col2ar.search('account.move', [
            ('journal_id', '=', inv_journal),
            ('state', '=', 'posted'),
            ('type', '=', 'out_invoice')
        ]
        )

    implided_ids = col2ar.migrate('account.move', domain=[
            ('id', 'in', move_ids),
        ])

    lines = col2ar.search('account.move.line', [('move_id', 'in', move_ids)])
    res = col2ar.migrate('account.move.line', domain=[('move_id', 'in', move_ids)])
    dest_moves = col2ar.get_result_ids(implided_ids)
    col2ar.execute_method_chunked('account.move', 'post', dest_moves, 'to')
    #col2ar.migrate('account.move', row_ids=move_ids, force_fields=col2ar.name_field_def())