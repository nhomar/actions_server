journal_id = env['account.journal'].search([('name','=','Saldos Iniciales')]) # Diario que tendrá los asientos
memo_account = journal_id
am_ids = am_obj = env['account.move']
aml_obj = env['account.move.line'].with_context(check_move_validity=False)
res = {}
for inv in records:
  if inv.x_galaxy_residual > 0.0:
    log('Factura sin Exceso - %s' % inv.id_galaxy, level='info')
    # Solo estamos haciendo esto para los excesos, cuando el saldo de la factura queda negativo en Galaxy.
    continue
  if inv.residual <= 0:
    log('Factura ya pagada - %s' % inv.id_galaxy, level='info')
    # Solo estamos haciendo esto para los excesos, cuando el saldo de la factura queda negativo en Galaxy.
    continue
  partner_id = env['res.partner']._find_accounting_partner(inv.partner_id)
  am_id = am_obj.create({
    'ref': 'Pago en Exceso aplicado sobre %s' % (inv.id_galaxy),
    'journal_id': journal_id.id,
    'date': '2018-12-31' # Asiento al Final del año
  })
  # Considerar la fecha del exceso para generar el valor del saldo contable. Preguntar qué hacer.
  currency_id = False
  amount_invoice = inv.amount_total 
  amount_invoice_currency = 0
  
  amount_remaining = -inv.x_galaxy_residual
  amount_remaining_currency = 0
  
  amount = inv.amount_total - inv.x_galaxy_residual  # inv.amount_total = 1000, inv.x_galaxy_residual = -5000 => amount = 6000
  amount_currency = 0
  
  if inv.company_currency_id != inv.currency_id:
    currency_id = inv.currency_id.id
    
    amount_invoice_currency = amount_invoice
    amount_remaining_currency = amount_remaining
    
    amount_invoice = inv.currency_id._convert(amount_invoice, inv.company_currency_id, inv.company_id, inv.date_invoice)
    amount_remaining = inv.currency_id._convert(amount_remaining, inv.company_currency_id, inv.company_id, inv.date_invoice)
    
    amount_currency = amount
    amount = amount_invoice + amount_remaining
  
  # Movimiento del Debito: La cuenta de Orden
  debit = aml_obj.create({
    'account_id': journal_id.default_debit_account_id.id,
    'move_id': am_id.id,
    'name': 'Asiento de Ajuste por Aplicado en Factura %s' % (inv.id_galaxy),
    'debit': amount,
    'credit': 0.0,
    'amount_currency': amount_currency,
    'currency_id': currency_id,
    'partner_id': partner_id.id,
  })
  
  # Movimiento del Credito: La cuenta por cobrar que se conciliara con la factura
  credit1 = aml_obj.create({
    'account_id': inv.account_id.id,
    'move_id': am_id.id,
    'name': 'Asiento Aplicado en Factura %s' % (inv.id_galaxy),
    'debit': 0.0,
    'credit': amount_invoice,
    'amount_currency': -amount_invoice_currency,
    'currency_id': currency_id,
    'partner_id': partner_id.id,
  })
  
  # Movimiento del Credito: La cuenta por cobrar que quedara libre para el futuro
  credit2 = aml_obj.create({
    'account_id': inv.account_id.id,
    'move_id': am_id.id,
    'name': 'Asiento de Ajuste por exceso en Factura %s' % (inv.id_galaxy),
    'debit': 0.0,
    'credit': amount_remaining,
    'amount_currency': -amount_remaining_currency,
    'currency_id': currency_id,
    'partner_id': partner_id.id,
  })
  
  am_id.post()
  
  # Aqui concilio a la factura con el valor correspondiente a su pago exacto.
  inv.register_payment(credit1)
  
  res[inv.id_galaxy] = credit1.id
  am_ids |= am_id
log('Asientos Creados - %s' % repr(res), level='info')
log('Asientos Creados - objetos - %s' % repr(am_ids), level='info')

# raise Warning('NO HAS TERMINADO')  
