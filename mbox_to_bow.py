import mailbox
import re
import email.utils
import pdb
import math
import logging
import collections
import numpy as np
import time
import datetime
import sklearn
import random
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import cross_val_score


def make_bow(mbox,num_words):
	if type(mbox) is str:
		mbox = mailbox.mbox(mbox)

	# define global bag of words
	global_text = []

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
			global_text = global_text + split_body
		except:
			logging.error('Could not get body of email' + str(msg['Subject']))
			continue

	global_bow = collections.Counter(global_text)
	# 14677 unique words
	global_bow_top = global_bow.most_common(num_words)

	global_bow_words = [x[0] for x in global_bow_top]

	# get dictionary of all words in order with 0's
	# viable_word_dict = dict.fromkeys(global_bow_words,0)

	bow_list = []
	for msg in mbox:
		msg_word_dict = dict.fromkeys(global_bow_words,0)
		try:
			body = get_body(msg)
			exclamaions = count_exclamations(body)
			body = replace_newlines(body)
			body = strip_punctuation(delete_nums(body)).lower()
			split_body = body.split(' ')
			for word in split_body:
				if word in msg_word_dict.keys():
					msg_word_dict[word] += 1
		except:
			logging.error('Could not get body of email' + str(msg['Subject']))
			bow_list.append(msg_word_dict)  # should be all 0's if gets here
			continue

		bow_list.append(msg_word_dict)

	# print len(bow_list)  # 2033

	bow_mat_list = []
	for entry in bow_list:
		bow_mat_list.append(entry.values())

	# big matrix with feature list for each email
	# rows = emails, columns = words
	bow_mat = np.array(bow_mat_list)

	# return matrix and list of words
	return bow_mat, global_bow_words	


def make_bow_given_dict(mbox,global_bow_words):
	bow_list = []
	for msg in mbox:
		msg_word_dict = dict.fromkeys(global_bow_words,0)
		try:
			body = get_body(msg)
			exclamaions = count_exclamations(body)
			body = replace_newlines(body)
			body = strip_punctuation(delete_nums(body)).lower()
			split_body = body.split(' ')
			for word in split_body:
				if word in msg_word_dict.keys():
					msg_word_dict[word] += 1
		except:
			logging.error('Could not get body of email' + str(msg['Subject']))
			bow_list.append(msg_word_dict)  # should be all 0's if gets here
			continue

		bow_list.append(msg_word_dict)

	# print len(bow_list)  # 2033

	bow_mat_list = []
	for entry in bow_list:
		bow_mat_list.append(entry.values())

	# big matrix with feature list for each email
	# rows = emails, columns = words
	bow_mat = np.array(bow_mat_list)

	# return matrix and list of words
	return bow_mat

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


def find_time(mbox):

	if type(mbox) is str:
		mbox = mailbox.mbox(mbox)

	pattern = "^(\[.+\]|\s|Re:|Fwd:)+"

	mailing_threads = {}
	emails = []

	for msg in mbox:
		emails.append(0)

		try:
			thread = re.sub(pattern, "", msg["Subject"])
		except:
			logging.error("Could not parse subject " + str(msg['Subject']))
			continue

		try:
			email_time = datetime.datetime.fromtimestamp(time.mktime(email.utils.parsedate(msg['Date'])))
		except:
			logging.error("Could not parse date or email: " + str(msg['Date']) + ", " + msg['From'])
			continue

		if thread not in mailing_threads:
			mailing_threads[thread] = []
		else:
			previous_email = mailing_threads[thread][len(mailing_threads[thread]) - 1]
			try:
				emails[previous_email[0]] = (email_time - previous_email[1]).total_seconds()
			except:
				logging.error("Issue updating email time")
				continue

		mailing_threads[thread].append((len(emails) - 1, email_time))

	return emails


def train_classifier(mbox,num_words):

	# split data
	split_pct = 0.6  # test-train split percent
	split = split_by_response(mbox)
	num_pos = len(split[0])
	num_neg = len(split[1])
	# print num_pos  # 611 scas
	# print num_neg  # 1441 scas
	pos_split_idx = int(num_pos * split_pct)
	neg_split_idx = int(num_neg * split_pct)

	# shuffle data - random.shuffle is in place
	pos_data = split[0]
	neg_data = split[1]
	random.shuffle(pos_data)
	random.shuffle(neg_data)

	# split data
	train_pos = pos_data[:pos_split_idx]
	train_neg = neg_data[:neg_split_idx]
	test_pos = pos_data[pos_split_idx:]
	test_neg = neg_data[neg_split_idx:]

	train_data = train_pos + train_neg
	test_data = test_pos + test_neg

	# print len(train_data)  # 1230
	# print len(test_data)  # 822

	# get data matrices - TRAIN DATA
	train_bow_mat, global_bow_words = make_bow(train_data, num_words)
	train_times = find_time(train_data)
	train_bool_responses = [1 if x > 0 else 0 for x in train_times]
	train_times = [x if x > 0 else float('Inf') for x in train_times]

	# get data matrices - TEST DATA
	test_bow_mat = make_bow_given_dict(test_data, global_bow_words)
	test_times = find_time(test_data)
	test_bool_responses = [1 if x > 0 else 0 for x in test_times]
	test_times = [x if x > 0 else float('Inf') for x in test_times]

	# transform to np arrays
	train_bool_responses = np.array(train_bool_responses)
	train_times = np.array(train_times)
	test_bool_responses = np.array(test_bool_responses)
	test_times = np.array(test_times)

	# train, evaluate, and test random forest
	train_scores = []
	test_scores = []
	for n in xrange(1,20):
		rf = RandomForestClassifier(n_estimators = n)
		rf.fit(train_bow_mat,train_bool_responses)
		scores.append(cross_val_score(rf,train_bow_mat,train_bool_responses,cv=10))
		test_scores.append(rf.score(test_bow_mat,test_bool_responses))


	# fig = plt.figure()
	# fig.add_subplot(1,1,1)
	# fig.set_size_inches(10,10)
	# sns.boxplot(scores)
	# plt.show()

	# print train_scores
	# for x in train_scores:
	# 	print sum(x) / float(len(x))

	print test_scores
	for x in test_scores:
		print sum(x) / float(len(x))

	# n = 6 and 16 are good? (random forest binary classifier)
	# have to split into test and train better though...

	# now evaluate on TEST DATA










	



