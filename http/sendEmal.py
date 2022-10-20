from email.mime.multipart import MIMEMultipart
import smtplib
from email.mime.text import MIMEText
from email.header import Header

SMTP_HOST='smtp.qq.com'
SMTP_PORT=465
SMTP_ADDR='qq.com'

USER='389830809'
PASS='emfeqitffxgabjgh'
TO=['tomchen0809@gmail.com','1056174101@qq.com']

__all__=['sendemail']

def sendemail(text):
    email_addr=USER+'@'+SMTP_ADDR,PASS
    smtp=smtplib.SMTP_SSL(host=SMTP_HOST)
    smtp.connect(host=SMTP_HOST,port=465)
    smtp.login(email_addr)
    msg=MIMEMultipart()
    msg['Subject']=Header('登录提醒','utf-8').encode()
    From= USER+' <'+email_addr+'>'
    msg['From']=From
    msg['To']=TO
    test=MIMEText(text,'plain','utf-8')
    msg.attach(test)
    smtp.sendmail(email_addr,
                TO,
                msg.as_string())
    smtp.quit()
    pass
    
