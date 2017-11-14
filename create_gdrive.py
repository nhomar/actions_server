# Esto debe ser creado en el modelo (para este ejemplo es en la sale order).

url = env['google.drive.config'].browse(ID(integer)ofconfig).get_google_drive_url(record.id, "ID-DOCUMENTxxxsssxxxx")
record.message_post(body="Calcula los costos del proyecto  <a href='%s' target='NEW'>aqui</a>" % url, message_type="comment", subtype="mail.mt_note")
