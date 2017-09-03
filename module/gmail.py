# -*- coding: utf-8 -*-
import smtplib  
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText

def send_email(subject, contents , account=None):  
    from_addr = 'haedong2017@gmail.com'
    
    if account == None:
        to_addr = 'genioustar@gmail.com,hayden4143@gmail.com,junhwanu@gmail.com'
    elif account == '5107243872' or account == '7003919272':
        to_addr = 'hayden4143@gmail.com'
    elif account == '5105855972':
        to_addr = 'junhwanu@gmail.com'
    elif account =='51115392':
        to_addr = 'jenioustar@gmail.com'

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()

    server.login(from_addr, 'goehddl00')

    body = MIMEMultipart()
    body['subject'] = subject
    body['From'] = from_addr
    body['To'] = to_addr

    html = ("<div>%s</div>" % str(contents))
    msg = MIMEText(html, '')
    body.attach(msg)

    server.sendmail(from_addr=from_addr,
                    to_addrs=[to_addr],  # list, str 둘 다 가능
                    msg=body.as_string())

    server.quit()
    
if __name__ == "__main__":
    send_email("test",'test','5107243872')
    