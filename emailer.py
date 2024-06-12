import smtplib
from email.message import EmailMessage
import tomllib  # requires Python 3.11
import pprint

def createAndSendEmailAlert(email_subject: str, email_body: str):
    """Read outgoing email info from a TOML config file and send an email alert."""
    try:
        with open(".env.toml", "rb") as file_object:
            secret_dict = tomllib.load(file_object)
        pprint.pprint(secret_dict)

        # Basic information
        host = secret_dict["outgoing_email_host"]
        port = secret_dict["outgoing_email_port"]
        outemail = secret_dict["outgoing_email_address"]
        outpwd = secret_dict["outgoing_email_password"]
        toemail = secret_dict["receiver_email_address"]

        # Create an instance of an EmailMessage
        msg = EmailMessage()
        msg["From"] = outemail
        msg["To"] = toemail
        msg["Reply-to"] = outemail
        msg["Subject"] = email_subject
        msg.set_content(email_body)

        print("========================================")
        print(f"Prepared Email Message: ")
        print("========================================")
        print()
        print(f"{str(msg)}")
        print("========================================")
        print()

        # Create an instance of an email server, enable debug messages
        server = smtplib.SMTP(host, port)
        server.set_debuglevel(2)

        print("========================================")
        print(f"SMTP server created: {str(server)}")
        print("========================================")
        print()

        try:
            server.starttls()
            print("========================================")
            print(f"TLS started. Will attempt to login.")
            print("========================================")
            print()

            try:
                server.login(outemail, outpwd)
                print("========================================")
                print(f"Successfully logged in as {outemail}.")
                print("========================================")
                print()

                server.send_message(msg)
                print("========================================")
                print(f"Message sent.")
                print("========================================")
                print()
            except Exception as e:
                print(f"Login or sending error: {str(e)}")
            finally:
                server.quit()
                print("========================================")
                print(f"Session terminated.")
                print("========================================")
                print()

        except Exception as e:
            print(f"Error connecting or starting TLS: {str(e)}")

    except Exception as e:
        print(f"Error reading secrets or creating message: {str(e)}")

if __name__ == "__main__":
    subject_str = "High Bidding Alert!"
    content_str = "Someone just bid above your bidding threshold!"

    email_message = createAndSendEmailAlert(
        email_subject=subject_str, email_body=content_str
    )
