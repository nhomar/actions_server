# Add all invoice addresses as followers of an invoice.
contacts = record.commercial_partner_id.child_ids.filtered(lambda p: p.type == 'invoice').ids
record.message_subscribe(contacts)
