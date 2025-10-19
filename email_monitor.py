
import imaplib
import email
from email.header import decode_header
from rain_report import read_config
import os

def connect_to_email(username, password, imap_url):
   try:
       mail = imaplib.IMAP4_SSL(imap_url)
       mail.login(username, password)
       print("连接成功")
       return mail
   except Exception as e:
       print(f"连接失败: {e}")
       return None


def search_emails(mail, folder="inbox", criteria="UNSEEN"):
   mail.select(folder)
   status, messages = mail.search(None, criteria)
   if status != "OK":
       print("搜索失败")
       return []
   return messages[0].split()


def parse_email(mail, message_id):
   status, data = mail.fetch(message_id, "(RFC822)")
   email_body = data[0][1]
   email_message = email.message_from_bytes(email_body)
   # 获取发件人
   from_header = decode_header(email_message["From"])[0]
   sender = from_header[0].decode(from_header[1]) if isinstance(from_header[0], bytes) else from_header[0]
   # 获取主题
   subject_header = decode_header(email_message["Subject"])[0]
   subject = subject_header[0].decode(subject_header[1]) if isinstance(subject_header[0], bytes) else subject_header[0]
   # 获取正文（仅处理纯文本部分）
   for part in email_message.walk():
       if part.get_content_type() == "text/plain":
           body = part.get_payload(decode=True).decode(part.get_content_charset())
           break
   # 将邮件设置为已读
   mail.store(message_id, "+FLAGS", "\\Seen")
   return {"sender": sender, "subject": subject, "body": body}

def save_attachments(email_message, save_dir="attachments"):
   if not os.path.exists(save_dir):
       os.makedirs(save_dir)
   for part in email_message.walk():
       if part.get_content_maintype() == "multipart":
           continue
       filename = part.get_filename()
       if filename:
           filepath = os.path.join(save_dir, filename)
           with open(filepath, "wb") as f:
               f.write(part.get_payload(decode=True))
           print(f"附件已保存: {filepath}")


# 连接邮箱
mailbox=read_config('ignore_file\\key.txt')
mail = connect_to_email(mailbox["mail_username"], mailbox["mail_password"], mailbox["mail_url"])
# 获取未读邮件数量
message_ids = search_emails(mail)
print(f"未读邮件数量: {len(message_ids)}")
# 获取所有邮件的内容
for msg_id in message_ids:
   email_info = parse_email(mail, msg_id)
   print(f"发件人: {email_info['sender']}, 主题: {email_info['subject']}, 正文: {email_info['body']}")


'''
# 示例：处理附件
for msg_id in message_ids:
   status, data = mail.fetch(msg_id, "(RFC822)")
   email_message = email.message_from_bytes(data[0][1])
   save_attachments(email_message)
'''