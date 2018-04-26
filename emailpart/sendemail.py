import base64
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from httplib2 import Http
from time import localtime, strftime, time, sleep
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client import file
from apiclient.discovery import build
from apiclient import errors


def upload_log(text):
	'''
	Upload the Alert time to the google drive sheet
	'''
	scope=['https://spreadsheets.google.com/feeds']
	credentials=ServiceAccountCredentials.from_json_keyfile_name('ProjectLog-41cafcffcf13.json', scope)
	gc=gspread.authorize(credentials)
	wks=gc.open('ISeeU_Log').sheet1
	wks.append_row([text])


def SendMessage(service, user_id, message):
	'''
	send the mime email package
	'''
	try:
		message = (service.users().messages().send(userId=user_id, body=message).execute())
		print ('Message Id: %s' % message['id'])
		return message
	except errors.HttpError, error:
		print ('An error occurred: %s' % error)


def create_message_with_attachment(sender, to, subject, message_text, file):
	'''
	Create the email
	Included information: Sender, Receiver, Subject, Text, Attached Image
	'''
	message = MIMEMultipart()
	message['to'] = to
	message['from'] = sender
	message['subject'] = subject

	msg = MIMEText(message_text)
	message.attach(msg)

	fp = open(file, 'rb')
	msg = MIMEImage(fp.read(), _subtype='jpeg')
	fp.close()
	
	filename = os.path.basename(file)
	msg.add_header('Content-Disposition', 'attachment', filename=filename)
	message.attach(msg)

	return {'raw': base64.urlsafe_b64encode(message.as_string())}

def main():

	SCOPES = 'https://mail.google.com'
	store = file.Storage('credentials.json')
	creds = store.get()
	if not creds or creds.invalid:
		flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
		creds = tools.run_flow(flow, store)
	service = discovery.build('gmail', 'v1', http=creds.authorize(Http()))
	
	nowtime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
	text = 'Alert at ' + nowtime
	upload_log(text)
	pic = 'guldan.jpg'
	sender = "wenganq11@gmail.com"
	to = "wengq@bu.edu"
	subject = "Gmail API"
	message = create_message_with_attachment(sender, to, subject, text, pic)
	SendMessage(service, 'me', message)


if __name__ == '__main__':
	main()


