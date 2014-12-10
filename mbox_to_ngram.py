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
from sklearn.svm import SVC


def make_ngram(mbox,num_words,n):
	if type(mbox) is str:
		mbox = mailbox.mbox(mbox)

	# define global ngram collection
	global_ngrams = []

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
			n_grams = process_ngrams(split_body,n)
			global_ngrams = global_ngrams + n_grams
		except:
			#logging.error('Could not get body of email' + str(msg['Subject']))
			continue

	global_ngrams = collections.Counter(global_ngrams)
	global_ngrams_top = global_ngrams.most_common(num_words)
	# print global_ngrams_top
	global_ngrams_words = [x[0] for x in global_ngrams_top]

	# get dictionary of all words in order with 0's
	# viable_word_dict = dict.fromkeys(global_ngrams_words,0)

	ngram_list = []
	for msg in mbox:
		msg_ngram_dict = dict.fromkeys(global_ngrams_words,0)
		try:
			body = get_body(msg)
			exclamaions = count_exclamations(body)
			body = replace_newlines(body)
			body = strip_punctuation(delete_nums(body)).lower()
			split_body = body.split(' ')
			n_grams = process_ngrams(split_body,n)

			for ngram in n_grams:
				if ngram in msg_ngram_dict.keys():
					msg_ngram_dict[ngram] += 1
		except:
			#logging.error('Could not get body of email' + str(msg['Subject']))
			ngram_list.append(msg_ngram_dict)  # should be all 0's if gets here
			continue

		ngram_list.append(msg_ngram_dict)

	# print len(ngram_list)  # 2033
	# print ngram_list
	print msg_ngram_dict

	ngram_mat_list = []
	for entry in ngram_list:
		ngram_mat_list.append(entry.values())

	# big matrix with feature list for each email
	# rows = emails, columns = words
	ngram_mat = np.array(ngram_mat_list)

	# return matrix and list of words
	return ngram_mat, global_ngrams_words	


def make_ngram_given_dict(mbox,global_ngrams_words):

	n = len(str.split(global_ngrams_words[0]))

	if type(mbox) is str:
		mbox = mailbox.mbox(mbox)

	ngram_list = []
	for msg in mbox:
		msg_ngram_dict = dict.fromkeys(global_ngrams_words,0)
		try:
			body = get_body(msg)
			exclamaions = count_exclamations(body)
			body = replace_newlines(body)
			body = strip_punctuation(delete_nums(body)).lower()
			split_body = body.split(' ')
			ngrams = process_ngrams(split_body,n)
			for ngram in ngrams:
				if ngram in msg_ngram_dict.keys():
					msg_ngram_dict[ngram] += 1
		except:
			#logging.error('Could not get body of email' + str(msg['Subject']))
			ngram_list.append(msg_ngram_dict)  # should be all 0's if gets here
			continue

		ngram_list.append(msg_ngram_dict)

	# print len(ngram_list)  # 2033

	ngram_mat_list = []
	for entry in ngram_list:
		ngram_mat_list.append(entry.values())

	# big matrix with feature list for each email
	# rows = emails, columns = words
	ngram_mat = np.array(ngram_mat_list)

	# return matrix
	return ngram_mat

def make_ngram_given_dict_string(input_str,global_ngrams_words):

	n = len(str.split(global_ngrams_words[0]))

	ngram_list = []
	msg_ngram_dict = dict.fromkeys(global_ngrams_words,0)

	body = input_str
	exclamaions = count_exclamations(body)
	body = replace_newlines(body)
	body = strip_punctuation(delete_nums(body)).lower()
	split_body = body.split(' ')
	ngrams = process_ngrams(split_body,n)
	for ngram in ngrams:
		if ngram in msg_ngram_dict.keys():
			msg_ngram_dict[ngram] += 1

	ngram_list.append(msg_ngram_dict)

	ngram_mat_list = []
	for entry in ngram_list:
		ngram_mat_list.append(entry.values())

	ngram_mat = np.array(ngram_mat_list)

	return ngram_mat	

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

def process_ngrams(words, n):
    # words = text.split()
    ngrams = zip(*[words[i:] for i in range(n)])
    return [''.join(x) for x in ngrams]

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
			#logging.error("Could not parse subject " + str(msg['Subject']))
			continue

		try:
			A_email = email.utils.parseaddr(msg['From'])[1]
		except:
			#logging.error("Could not parse date or email: " + str(msg['Date']) + ", " + msg['From'])
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
			#logging.error("Could not parse subject " + str(msg['Subject']))
			continue

		try:
			email_time = datetime.datetime.fromtimestamp(time.mktime(email.utils.parsedate(msg['Date'])))
		except:
			#logging.error("Could not parse date or email: " + str(msg['Date']) + ", " + msg['From'])
			continue

		if thread not in mailing_threads:
			mailing_threads[thread] = []
		else:
			previous_email = mailing_threads[thread][len(mailing_threads[thread]) - 1]
			try:
				emails[previous_email[0]] = (email_time - previous_email[1]).total_seconds()
			except:
				#logging.error("Issue updating email time")
				continue

		mailing_threads[thread].append((len(emails) - 1, email_time))

	return emails


def train_classifier(mbox,num_words,n):

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
	train_pos_labels = [1]*len(train_pos)
	train_neg_labels = [0]*len(train_neg)
	test_pos_labels = [1]*len(test_pos)
	test_neg_labels = [0]*len(test_neg)
	
	train_data = train_pos + train_neg
	test_data = test_pos + test_neg
	train_labels = train_pos_labels + train_neg_labels
	test_labels = test_pos_labels + test_neg_labels

	# print len(train_data)  # 1230
	# print len(test_data)  # 822

	# get data matrices - TRAIN DATA
	train_ngram_mat, global_ngrams_words = make_ngram(train_data, num_words, n)
	print train_ngram_mat
	train_times = find_time(train_data)
	train_bool_responses = [1 if x > 0 else 0 for x in train_times]
	train_times = [x if x > 0 else float('Inf') for x in train_times]

	# get data matrices - TEST DATA
	test_ngram_mat = make_ngram_given_dict(test_data, global_ngrams_words)
	print test_ngram_mat
	test_times = find_time(test_data)
	test_bool_responses = [1 if x > 0 else 0 for x in test_times]
	test_times = [x if x > 0 else float('Inf') for x in test_times]

	# transform to np arrays
	train_bool_responses = np.array(train_bool_responses)
	train_times = np.array(train_times)
	test_bool_responses = np.array(test_bool_responses)
	test_times = np.array(test_times)

	### Not sure if Willy's function returns the correct thing for list of emails
	### Going to use test_bools and train_bools instead of _responses for now
	train_bool_responses = np.array(train_labels)
	train_weights = train_bool_responses + 1  # should be 2's and 1's
	test_bool_responses = np.array(test_labels)

	classifiers = []

	# print train_ngram_mat
	# print len(train_ngram_mat)
	# print np.amax(train_ngram_mat)
	# print global_ngrams_words

	# train, evaluate, and test random forest
	rf_train_scores = []
	rf_test_scores = []
	for n in xrange(1,20):  # initial results show this is the best? PLOT!
		rf = RandomForestClassifier(n_estimators=n)
		rf.fit(train_ngram_mat,train_bool_responses,sample_weight=train_weights)
		rf_train_scores.append(cross_val_score(rf,train_ngram_mat,train_bool_responses,cv=10))
		rf_test_scores.append(rf.score(test_ngram_mat,test_bool_responses))

	# train, evaluate, and test SVM
	svm_train_scores = []
	svm_test_scores = []
	svm = SVC(C=1.0,kernel='linear',probability=True,class_weight='auto')  # change probability to True?
	svm.fit(train_ngram_mat,train_bool_responses)
	svm_train_scores.append(cross_val_score(svm,train_ngram_mat,train_bool_responses,cv=10))
	svm_test_scores.append(svm.score(test_ngram_mat,test_bool_responses))

	## Random Forest Stats
	# print rf_train_scores
	# for x in rf_train_scores:
	# 	print sum(x) / float(len(x))

	# print rf_test_scores

	## SVM Stats
	# print svm_train_scores
	# for x in svm_train_scores:
	# 	print sum(x) / float(len(x))

	# print svm_test_scores
	# print rf.predict(test_ngram_mat)
	# print svm.predict(test_ngram_mat)
	
	# add classifiers to list

	# print rf.get_params()

	classifiers.append(rf)
	classifiers.append(svm)

	return classifiers, global_ngrams_words

	# n = 6 and 16 are good? (random forest binary classifier)
	# have to split into test and train better though...


def evaluate_classifiers(classifiers,global_ngrams_words,input_message):
	
	# transform input message to matrix
	input_bow_mat = make_ngram_given_dict_string(input_message, global_ngrams_words)
	# print input_bow_mat

	for classifier in classifiers:
		print classifier.predict(input_bow_mat)


def run_all(mbox,num_words,n):

	input_message = "hey all i hope you're doing well. please respond to this message at your earliest convenience. scas scas scas scas respond respond respond willy anna long message here please respond respond asap asap asap asap asap why aren't you responding responses give me more data to crunch this classifier really doesn't seem to like short messages don't know what's going on please respond respond respond respond scas scas money budget budget budget hungry harvard me you you you you email office have at with a in you and of to the the to and of you a in in for scas is this be on if with will are do by director director by do more know harvard our our our important urgent board summer committee questions clients great court them room mailing information dont pbh free pbh hi when small time one hey come would hours people questions service its its its comp comp comp when legal interest guys school join join mail boston message"

	classifiers, global_ngrams_words = train_classifier(mbox,num_words,n)
	evaluate_classifiers(classifiers,global_ngrams_words,input_message)





	



