
# import datetime
# import schedule
# import time
# from email.message import EmailMessage
# import ssl
# import smtplib
# import pause
# import sched


# sender = 'jjuliamaxxx@gmail.com'
# receiver = 'jjuliamaxxx@gmail.com'
# password = 'lguvzwzsishpgtbf'
# subject = 'Testing'
# body = """Ran Okay"""
# em = EmailMessage()
# em['From'] = sender
# em['To'] = receiver
# em['Subject'] = subject


# send_date = datetime.date(2023, 4, 11)
# send_time = datetime.time(13, 37)

# # create a scheduler object
# scheduler = sched.scheduler(time.time, time.sleep)


# def send_email():
#     # create the email message
#     em.set_content(body)

#     context = ssl.create_default_context()

#     with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
#         smtp.login(sender, password)
#         # connect to the SMTP server
#         # send the email
#         smtp.sendmail(sender, receiver, em.as_string())
#         smtp.quit()

#         print("Email sent!")


# # calculate the time to send the email
# send_datetime = datetime.datetime.combine(send_date, send_time)
# send_timestamp = time.mktime(send_datetime.timetuple())

# # schedule the email to be sent at the specified time
# scheduler.enterabs(send_timestamp, 1, send_email)

# print('running')
# # run the scheduler
# scheduler.run()
