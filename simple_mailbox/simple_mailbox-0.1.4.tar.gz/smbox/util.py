__author__ = 'gaojian'
__date__ = '12/4/14'

import imaplib
import email

def get_email(host, user, sender):
    '''using imaplib to connect to an imap server and fetch the qualified email: search the INBOX for the latest email from sender.
    host : 'imap.126.com'
    user : ('username@example.com', 'password')
    sender : 'sender@example.com'
    return : email_message
    '''
    cnt, latest_email_id = get_latest_email_id(host, sender, user)
    result, data = cnt.fetch(latest_email_id, "(RFC822)")  # fetch the email body (RFC822) for the given ID
    raw_email = data[0][1]  # here's the body, which is raw text of the whole email
    cnt.logout()
    email_message = email.message_from_string(raw_email)
    return email_message

# note that if you want to get text content (body) and the email contains
# multiple payloads (plaintext/ html), you must parse each message separately.
# use something like the following: (taken from a stackoverflow post)
def get_first_text_block(email_message_instance):
    maintype = email_message_instance.get_content_maintype()
    if maintype == 'multipart':
        for part in email_message_instance.get_payload():
            if part.get_content_maintype() == 'text':
                return part.get_payload()
    elif maintype == 'text':
        return email_message_instance.get_payload()


def get_latest_email_id(host, sender, user):
    cnt = imaplib.IMAP4_SSL(host=host)
    cnt.login(*user)
    cnt.select("INBOX")
    result, data = cnt.search(None, '(FROM "%s")' % sender)
    ids = data[0]  # data is a list.
    id_list = ids.split()  # ids is a space separated string
    latest_email_id = id_list[-1]  # get the lates
    return cnt, latest_email_id


def delete_email_from_mail_box(host, user, sender):
    cnt, latest_email_id = get_latest_email_id(host, sender, user)
    cnt.store(latest_email_id, '+FLAGS', '\\Deleted')
    cnt.expunge()
    cnt.logout()

if __name__ == '__main__':
    host = 'imap.126.com'
    user = ('gjstar@126.com', 'gj660510')
    sender = 'ushernetwork@microstrategy.com'

    email_msg = get_email(host=host, user=user, sender=sender)
    print get_first_text_block(email_msg)
    delete_email_from_mail_box(host=host, user=user, sender=sender)


