# put the id of your payment journal here
journal_id = 10

voucher_obj = env['account.voucher']
so_obj = env['sale.order']
so = so_obj.search([('name','=',object.reference)], limit=1)
for inv in so.invoice_ids:
    env['account.invoice'].signal_workflow([inv.id], 'invoice_open')
    context = dict(context or {})
    context.update({
        'invoice_id': inv.id,
        'invoice_type': inv.type,
        'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
        'payment_expected_currency': inv.currency_id.id,
        'default_partner_id': env['res.partner']._find_accounting_partner(inv.partner_id).id,
        'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
        'default_reference': inv.name,
        'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
        'default_journal_id': journal_id
        })

    default_keys = [vdk for vdk in voucher_obj._defaults.keys()]
    vals = voucher_obj.with_context(context).default_get(default_keys)
    onchange_date_vals = voucher_obj.with_context(context).onchange_date(
        [], vals['date'], vals['currency_id'],
        vals['payment_rate_currency_id'], vals['amount'],
        vals['company_id'])['value']
    vals.update(onchange_date_vals)

    onchange_partner_vals = voucher_obj.with_context(context).onchange_partner_id(
        [], vals['partner_id'], vals['journal_id'], vals['amount'],
        vals['currency_id'], vals['type'], False)['value']
    vals.update(onchange_partner_vals)

    onchange_amount_vals = voucher_obj.with_context(context).onchange_amount(
        [], vals['amount'], vals['payment_rate'], vals['partner_id'],
        vals['journal_id'], vals['currency_id'], vals['type'], vals['date'],
        vals['payment_rate_currency_id'], vals['company_id'])['value']
    vals.update(onchange_amount_vals)

    onchange_journal_vals = voucher_obj.with_context(context).onchange_journal(
        [], vals['journal_id'], vals['line_cr_ids'], False, vals['partner_id'],
        vals['date'], vals['amount'], vals['type'],
        vals['company_id'])['value']
    vals.update(onchange_journal_vals)

    vals['line_cr_ids'] = [(0, 0, x) for x in vals['line_cr_ids']]
    vals['line_dr_ids'] = [(0, 0, x) for x in vals['line_dr_ids']]

    voucher_id = voucher_obj.with_context(context).create(vals)
    voucher_obj.with_context(context).button_proforma_voucher([voucher_id])
