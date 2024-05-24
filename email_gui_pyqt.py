import logging
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QTextEdit, QVBoxLayout, QWidget, QPushButton, QMessageBox, QFileDialog
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email_utils import send_email, LoginFailedException
import asyncio
import os
import sys

logging.basicConfig(level=logging.DEBUG)

class EmailSenderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.async_runner = None

    def initUI(self):
        layout = QVBoxLayout()

        subject_label = QLabel("Subject:")
        layout.addWidget(subject_label)
        self.subject_line = QLineEdit()
        layout.addWidget(self.subject_line)

        content_label = QLabel("Content:")
        layout.addWidget(content_label)
        self.content_text = QTextEdit()
        layout.addWidget(self.content_text)

        self.select_img_button = QPushButton("Embed Image")
        self.select_img_button.clicked.connect(self.select_image)
        layout.addWidget(self.select_img_button)

        select_attachment_button = QPushButton("Attach File")
        select_attachment_button.clicked.connect(self.select_attachment)
        layout.addWidget(select_attachment_button)

        send_button = QPushButton("Send Email")
        send_button.clicked.connect(self.send_email_pyqt)
        layout.addWidget(send_button)

        self.setLayout(layout)

    async def send_email_async(self, email_list, subject, content, attachments, embedded_images):
        try:
            logging.debug("Sending email asynchronously...")
            await send_email(email_list, subject, content, attachments, embedded_images)
            # Display confirmation message
            QMessageBox.information(self, "Confirmation", "Test email sent. Continue with the whole list?")
        except LoginFailedException as e:
            logging.error(f"Login failed: {e}")
            QMessageBox.warning(self, "Login Failed", f"SMTP Authentication Error: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def send_email_pyqt(self):
        subject = self.subject_line.text()
        content = self.content_text.toPlainText()
        attachments = [self.file_attachment] if hasattr(self, 'file_attachment') else []
        embedded_images = [self.img_attachment] if hasattr(self, 'img_attachment') else []

        # Step 1: Send Test Email
        asyncio.run(self.send_email_async(["danielamonicag@yahoo.com"], subject, content, attachments, embedded_images))

    def select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_name:
            with open(file_name, 'rb') as f:
                img_data = f.read()
            self.img_attachment = MIMEImage(img_data, name=os.path.basename(file_name), _subtype='jpeg')
            self.img_attachment.add_header('Content-ID', '<image1>')
            self.select_img_button.setDisabled(True)

    def select_attachment(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)")
        if file_name:
            with open(file_name, 'rb') as f:
                file_data = f.read()
            self.file_attachment = MIMEApplication(file_data, name=os.path.basename(file_name))

def main():
    app = QApplication(sys.argv)
    ex = EmailSenderApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
