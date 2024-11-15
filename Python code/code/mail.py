from email.mime.multipart import MIMEMultipart  # For creating a multipart email
from email.mime.text import MIMEText  # For adding the body text to the email
from email.mime.base import MIMEBase  # For handling attachments
from email import encoders  # For encoding attachments
import socket  # For checking internet connection
import smtplib  # For sending emails
import os  # For removing the attachment file after sending the email

def check_internet_connection():
    try:
        # Try to connect to a well-known website to check for internet connection
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        return False


def send_email_with_attachment(subject, body, recipients, cc_recipients, attachment_path):
    server = None  # Initialize server variable with None
    try:
        # Create a multipart message
        msg = MIMEMultipart()
        msg['From'] = 'extrashaikh786@gmail.com'  # Replace with your email address
        msg['To'] = ", ".join(recipients)
        msg['Cc'] = ", ".join(cc_recipients)
        msg['Subject'] = subject

        # Add body to the email
        msg.attach(MIMEText(body, 'plain'))

        # Attach the file
        with open(attachment_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {attachment_path}')

        msg.attach(part)

        # Connect to SMTP server (for example, Gmail's SMTP server)
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)  # Change to your SMTP server
            #server.set_debuglevel(1)  # Enable debugging
            server.starttls()
            # Login to your email account
            try:
                server.login('', '')  # Replace with your email and password
            except smtplib.SMTPAuthenticationError:
                print("Authentication failed. Check your email and password.")
                return
            # Send email
            recipients_with_cc = recipients + cc_recipients
            try:
                server.sendmail('', recipients_with_cc, msg.as_string())
                print("\033[92mEmail sent successfully to {}\033[0m with \033[92mCC to {}\033[0m".format(", ".join(recipients), ", ".join(cc_recipients)))
                print("\033[92mProgram has been successfully ran, Congratulations\033[0m")
                os.remove(attachment_path)
                
            except Exception as send_error:
                print("An error occurred while sending email:", send_error)
                return
        except smtplib.SMTPConnectError as smtp_connect_error:
            print("Failed to connect to SMTP server:", smtp_connect_error)
            return
        except Exception as server_error:
            print("An error occurred while connecting to SMTP server:", server_error)
            return
        finally:
            if server is not None:
                server.quit()  # Check if server is not None before calling quit()
    except Exception as e:
        print("An unexpected error occurred:", e)

