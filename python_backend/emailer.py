import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import bs4



def send_email(confirmationKey, email, name, username):
    port = 465  # For SSL
    f = open('./python_backend/credentials.json')

    credentials = json.load(f)

    # Create a secure SSL context
    context = ssl.create_default_context()

    # load the file
    with open("./python_backend/pages/email.html") as f:
        txt = f.read()
        soup = bs4.BeautifulSoup(txt)
    hiTag = soup.select('div.u-row-container:nth-child(4) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > div:nth-child(1) > p:nth-child(1) > span:nth-child(1)')
    hiTag[0].append(' ' + name + ',')
    
    buttonTag = soup.select('div.u-row-container:nth-child(4) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > table:nth-child(2) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(1) > div:nth-child(1) > a:nth-child(1)')
    buttonTag[0]['href'] = "http://10.49.2.23:5000/confirmEmail?confirmationKey=" + confirmationKey + "&username=" + username
    html_content = soup.prettify()
    sender_email = "spacewalkapp@gmail.com"
    receiver_email = email
    message = """\
    Subject: Hackathon test email

    This message is sent from Python server - test for hackathon flask server emailer."""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Space Walk - Confirm Your Email"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    htmlemail = MIMEText(html_content, 'html')

    msg.attach(htmlemail)

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("spacewalkapp@gmail.com", credentials["password"])
        server.sendmail(sender_email, receiver_email, msg.as_string())

if __name__ == "__main__":
  send_email("test","dam342@cornell.edu","Duncan")