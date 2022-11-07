from email.mime.multipart import MIMEMultipart
import smtplib
from email.mime.text import MIMEText
from email.header import Header

smtp=smtplib.SMTP_SSL(host='smtp.qq.com')
smtp.connect(host='smtp.qq.com',port=465)
smtp.login('389830809@qq.com','emfeqitffxgabjgh')
msg=MIMEMultipart()
msg['Subject']=Header('测试','utf-8').encode()
msg['From']='389830809 <389830809@qq.com>'
msg['To']='tomchen0809@gmail.com'
test=MIMEText('测试','plain','utf-8')
msg.attach(test)
smtp.sendmail('389830809@qq.com',
              'tomchen0809@gmail.com',
              msg.as_string())
smtp.quit()

