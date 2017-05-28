# Notify tuna if there is a new order placed.

import sendgrid
import os
from sendgrid.helpers.mail import *

with open('mail_template.txt', 'r') as f:
    template = f.read()

def notify(order_id, values):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("orders@tuna.tsinghua.edu.cn")
    to_email = Email("peiran.yao@tuna.tsinghua.edu.cn")
    subject = "A new order #{} has been placed.".format(order_id)
    content = Content("text/plain", template.format(*values))
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
