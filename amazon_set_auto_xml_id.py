## Model: amazon.product.ept

for r in records:
  if not r.product_tmpl_id.default_code:
    raise Warning('The product %s need a default code (reference) before publish on amazon.' % r.name)
  xml_id = env['ir.model.data'].sudo().search([('res_id', '=', r.product_tmpl_id.id), ('model', '=', 'product.template')])
  if not xml_id:
    raise Warning('Please set an xml_id to the product before go to amazon.')
  env['ir.model.data'].sudo().create({
    'name': xml_id.name,
    'module': 'auto',
    'res_id': r.id,
    'model': 'amazon.product.ept',
  })
