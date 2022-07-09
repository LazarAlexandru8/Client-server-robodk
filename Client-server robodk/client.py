import smtplib
from string import Template
from tkinter import *
from flask.json import jsonify
from requests import get, post
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

serverUrl = 'http://localhost:1234/'
host_email = '###@outlook.com'
host_password = '###'

# set up the SMTP server
s = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
s.starttls()


def createWindow(nr_robots):
    print(nr_robots)
    window = Tk()
    window.title("Misca Robotul")
    window.geometry('640x480')
    lbl = Label(window, text="Selectati robotul pe care doriti sa il miscati")
    lbl.grid(column=0, row=0)
    for index in range(nr_robots):
        print(index)
        btn = Button(window, text="Misca robotul " + str(index),
                     command=createMover(index))
        btn.grid(column=index + 1, row=2)

    window.mainloop()


def getNrRobots():
    return get(serverUrl).json()['robots']


def moveRobot(index):
    response = post(serverUrl, json={'robot': index})
    print(response.text)
    names, emails = get_contacts('./contacts.txt')  # read contacts
    message_template = read_template('./message.txt')
    s.login(host_email, host_password)
    for name, email in zip(names, emails):
        msg = MIMEMultipart()       # create a message

        # add in the actual person name to the message template
        message = message_template.substitute(
            PERSON_NAME=name.title(), INDEX=index)

        # setup the parameters of the message
        msg['From'] = host_email
        msg['To'] = email
        msg['Subject'] = "Atentionare!"

        # add in the message body
        msg.attach(MIMEText(message, 'plain'))

        # send the message via the server set up earlier.
        s.send_message(msg)

        del msg
    return response


def createMover(index):
    i = index
    return lambda: moveRobot(i)


def get_contacts(filename):
    names = []
    emails = []
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            names.append(a_contact.split()[0])
            emails.append(a_contact.split()[1])
    return names, emails


def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)


createWindow(getNrRobots())
