import mailbox
import re
import email.utils
import pdb
import math
import logging

def make_bow(mbox):
	if type(mbox) is str:
		mbox = mailbox.mbox(mbox)

	for msg in mbox:
		try:
			body = get_body(msg)
			print count_exclamations(body)
		except:
			logging.error('Could not get body of email' + str(msg['Subject']))
			continue

def get_body(msg):
	body = None
	# step through until not multipart; take that part as text
	if msg.is_multipart():
		for part in msg.walk():
			if part.is_multipart():
				for subpart in part.walk():
					if subpart.get_content_type() == 'text/plain':
						body = subpart.get_payload(decode=True)
			elif part.get_content_type() == 'text/plain':
				body = part.get_payload(decode=True)
	# if not multipart to begin with, take payload as text
	elif msg.get_content_type() == 'text/plain':
		body = msg.get_payload(decode=True)
	return body

def count_exclamations(body):
	return body.count('!')