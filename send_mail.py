# import smtplib
# # from email.mime.text import MIMEText
# from flask_mail import Mail
# import smtplib

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_mail(name, regNo, user_password, email, course):
    sender_email = ""
    receiver_email = email
    password = ""

    message = MIMEMultipart("alternative")
    message["Subject"] = "Campus News App User Credentials"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    text = "Name: "+name+"\n\nRegistration No.: "+regNo+"\n\nPassword: " + \
        user_password+"\n\nEmail: "+email+"\n\nCourse Offering: "+course
    html = f"<h2>Campus News App User Credentials</h2><ul><li><b>Name:</b> {name}</li><br><li><b>Registration No.:</b> {regNo}</li><br><li><b>Password:</b> {user_password}</li><br><li><b>Email:</b> {email}</li><br><li><b>Course Offering:</b> {course}</li><br></ul>"

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
