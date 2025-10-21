import imaplib
import email
from email.header import decode_header
import os
from auth_service.auth_decorator import require_secret


class email_monitor:
    def __init__(self):
        self.mail = None  # 添加实例变量来保存连接

    @require_secret("email_monitor", "password")
    def email_monitor_password(self, secret=None):
        return secret

    @require_secret("email_monitor", "username")
    def email_monitor_username(self, secret=None):
        return secret

    @require_secret("email_monitor", "url")
    def email_monitor_url(self, secret=None):
        return secret

    def connect_to_email(self):
        try:
            if self.mail is None:
                self.mail = imaplib.IMAP4_SSL(self.email_monitor_url())
                self.mail.login(self.email_monitor_username(), self.email_monitor_password())
                print("连接成功")
            return self.mail
        except Exception as e:
            print(f"连接失败: {e}")
            self.mail = None
            return None

    def search_emails(self, folder="inbox", criteria="UNSEEN"):
        mail = self.connect_to_email()
        if mail is None:
            return []

        try:
            status, _ = mail.select(folder)
            if status != "OK":
                print(f"选择文件夹 {folder} 失败")
                return []

            status, messages = mail.search(None, criteria)
            if status != "OK":
                print("搜索邮件失败")
                return []

            return messages[0].split()
        except Exception as e:
            print(f"搜索邮件时出错: {e}")
            return []

    def parse_email(self, message_id):
        mail = self.connect_to_email()
        if mail is None:
            return None

        try:
            status, data = mail.fetch(message_id, "(RFC822)")
            if status != "OK":
                print(f"获取邮件 {message_id} 失败")
                return None

            email_body = data[0][1]
            email_message = email.message_from_bytes(email_body)

            # 获取发件人
            from_header = decode_header(email_message["From"])[0]
            sender = from_header[0].decode(from_header[1]) if isinstance(from_header[0], bytes) else from_header[0]

            # 获取主题
            subject_header = decode_header(email_message["Subject"])[0]
            subject = subject_header[0].decode(subject_header[1]) if isinstance(subject_header[0], bytes) else \
            subject_header[0]

            # 获取正文（仅处理纯文本部分）
            body = ""
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body_bytes = part.get_payload(decode=True)
                    if body_bytes:
                        charset = part.get_content_charset() or 'utf-8'
                        try:
                            body = body_bytes.decode(charset)
                        except UnicodeDecodeError:
                            body = body_bytes.decode('utf-8', errors='ignore')
                    break

            # 将邮件设置为已读
            mail.store(message_id, "+FLAGS", "\\Seen")
            return {"sender": sender, "subject": subject, "body": body}

        except Exception as e:
            print(f"解析邮件 {message_id} 时出错: {e}")
            return None

    def save_attachments(self, email_message, save_dir="attachments"):
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

    def check_emailbox(self):
        # 获取未读邮件数量
        unseen_emails = self.search_emails()  # 修复：使用正确的变量名
        print(f"未读邮件数量: {len(unseen_emails)}")

        # 获取所有邮件的内容
        for msg_id in unseen_emails:  # 修复：使用正确的变量名
            email_info = self.parse_email(msg_id)
            if email_info:
                print(f"发件人: {email_info['sender']}")
                print(f"主题: {email_info['subject']}")
                print(f"正文: {email_info['body'][:100]}...")  # 只显示前100个字符

    def close_connection(self):
        """关闭IMAP连接"""
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
            except:
                pass
            finally:
                self.mail = None

    def email_service(self,arg1):
        # 创建邮箱监控实例
        monitor = email_monitor()

        try:
            # 测试连接
            print("正在连接邮箱服务器...")
            if monitor.connect_to_email():
                print("邮箱连接成功！")
            else:
                print("邮箱连接失败，请检查配置。")
                return

            # 检查邮箱
            print("\n开始检查邮箱...")
            monitor.check_emailbox()

        except KeyboardInterrupt:
            print("\n程序被用户中断")
        except Exception as e:
            print(f"程序运行出错: {e}")
        finally:
            # 确保关闭连接
            print("正在关闭邮箱连接...")
            monitor.close_connection()
            print("程序退出")

'''
# 示例：处理附件
for msg_id in message_ids:
   status, data = mail.fetch(msg_id, "(RFC822)")
   email_message = email.message_from_bytes(data[0][1])
   save_attachments(email_message)
'''