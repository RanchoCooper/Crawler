# -*- coding: utf-8 -*-
'''
des:

import同级文件夹内的mail163.py文件
--------
usage:

import mail163
mail = mail163.Mail(receiver='example@XXX.com')
mail.send(sub='Event', content='Something happened. Do have a check ASAP.')
--------

Mail(receiver='example@xxx.com')定义一个邮件接收者
mail=mail163.Mail(receiver='example@XXX.com')实例化
mail.send(sub='Event', content='Something happened. Do have a check ASAP.')
sub--邮件主题，content--邮件正文
'''
import smtplib
from email.mime.text import MIMEText


class Mail:

    def __init__(self, receiver):
        self.receiver = receiver

    def send(self, sub='Event', content='Something happened. Do have a check on your program ASAP.'):
        mailto_list = [self.receiver]   # 收件人邮箱
        mail_host = "smtp.163.com"
        mail_user = "wangadminzhi@163.com"  # 发件人邮箱
        mail_pass = "xway9999"  # 发件人密码(授权码)
        me = "Alert"+"<"+mail_user+">"
        msg = MIMEText(content, _subtype='plain', _charset='utf-8')     # 邮件正文
        msg['Subject'] = sub    # 邮件主题
        msg['From'] = me
        try:
            server = smtplib.SMTP()
            server.connect(mail_host)
            server.login(mail_user, mail_pass)
            server.sendmail(me, mailto_list, msg.as_string())
            server.close()
            return True
        except Exception, e:
            print str(e)
            return False
