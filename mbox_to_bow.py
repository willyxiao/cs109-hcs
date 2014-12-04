import mailbox
import re
import email.utils
import pdb
import math
import logging
import collections

def make_bow(mbox):
	if type(mbox) is str:
		mbox = mailbox.mbox(mbox)

	# define global bag of words
	global_bow = collections.Counter()

	for msg in mbox:
		try:
			body = get_body(msg)
			exclamations = count_exclamations(body)
			# strip newlines, make lowercase
			# strip punctuation, remove numbers on their own,
			body = replace_newlines(body)
			body = strip_punctuation(delete_nums(body)).lower()
			# split on spaces
			split_body = body.split(' ')
			bow = collections.Counter(split_body)
			global_bow = collections.Counter(bow,global_bow)
			print global_bow
			# strip punctuation after counting exclamations
			# lowercase everything
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

def strip_punctuation(body):
	return re.sub(r'[^\w\s]', '', body)

def delete_nums(body):
	return re.sub(' \d+', '', body)

def replace_newlines(body):
	return body.replace('\n',' ')

def split_by_response(mbox):
	if type(mbox) is str:
		mbox = mailbox.mbox(mbox)

	pattern = "^(\[.+\]|\s|Re:|Fwd:)+"
	responded = []
	no_response = []
	mailing_threads = {}

	for msg in mbox:
		try:
			thread = re.sub(pattern, "", msg["Subject"])
		except:
			logging.error("Could not parse subject " + str(msg['Subject']))
			continue

		try:
			A_email = email.utils.parseaddr(msg['From'])[1]
		except:
			logging.error("Could not parse date or email: " + str(msg['Date']) + ", " + msg['From'])
			continue

	if thread not in mailing_threads:
		mailing_threads[thread] = []

	mailing_threads[thread].append(msg)

	for i in mailing_threads:
		if len(mailing_threads[i]) > 1:
			responded.append(mailing_threads[i])
		else:
			no_response.append(mailing_threads[i])

	responded = sum(responded, [])
	no_response = sum(no_response, [])

	split = (responded, no_response)

	return split
