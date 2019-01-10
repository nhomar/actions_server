# Available variables:
#  - env: Odoo Environment on which the action is triggered
#  - model: Odoo Model of the record on which the action is triggered; is a void recordset
#  - record: record on which the action is triggered; may be void
#  - records: recordset of all records on which the action is triggered in multi-mode; may be void
#  - time, datetime, dateutil, timezone: useful Python libraries
#  - log: log(message, level='info'): logging function to record debug information in ir.logging table
#  - Warning: Warning Exception to use with raise
# To return an action, assign: action = {...}

if not env.user.has_group('__export__.res_groups_73_bd91e8f1'):
  raise Warning('You are not in the group.')

for r in records:
  move = r.move_id
  old = str(move.read([]))
  old_lines = str(move.line_ids.read([]))
  move.button_cancel()
  move.write({"date": '2019-01-01', 'ref': 'INITIAL: %s' % r.origin})
  for m in move.line_ids.filtered(lambda x: x.account_id.id == 634):
      m.write({'account_id': 944})
    
  move.action_post()
  log('User: %s Set move: %s - Lines: %s' % (env.user.name, old, old_lines), level="INITIAL BALANCE CUSTOMERS")
  r.message_post(body='Set as initial balance')

# raise Warning("Not implemented Yet")
