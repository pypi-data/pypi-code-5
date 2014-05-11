'''
Created on Aug 7, 2013

@author: karthicm
'''
# Import smtplib for the actual sending function
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import os
import utils_constants

# Create the container (outer) email message.
msg = MIMEMultipart()
msg['Subject'] = utils_constants.SUBJECT

msg['From'] = utils_constants.SENDER
msg['To'] = utils_constants.RECIPIENT
msg['Bcc'] = utils_constants.DEVELOPER
msg.preamble = utils_constants.TEST_DESCRIPTION

# Assume we know that the image files are all in PNG format
part = MIMEBase('application', "octet-stream")
part.set_payload( open(utils_constants.FINAL_RESULT_FILE,"rb").read())
Encoders.encode_base64(part)
part.add_header('Content-Disposition', 'attachment; filename="%s"'% os.path.basename(utils_constants.FINAL_RESULT_FILE))
msg.attach(part)


# Send the email via our own SMTP server.
s = smtplib.SMTP(utils_constants.SMTP_SERVER)
s.sendmail(utils_constants.SENDER, utils_constants.RECIPIENT, msg.as_string())
s.quit()