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
import sklearn.grid_search


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

    global_bow = collections.Counter(global_text)  # 14677 unique words
    global_bow_top = global_bow.most_common(num_words)

    global_bow_words = [x[0] for x in global_bow_top]

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

    bow_mat_list = []
    for entry in bow_list:
        bow_mat_list.append(entry.values())

    # big matrix with feature list for each email
    # rows = emails, columns = words
    bow_mat = np.array(bow_mat_list)

    # return matrix and list of words
    return bow_mat, global_bow_words    


def make_bow_given_dict(mbox,global_bow_words):

    if type(mbox) is str:
        mbox = mailbox.mbox(mbox)

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

    bow_mat_list = []
    for entry in bow_list:
        bow_mat_list.append(entry.values())

    # big matrix with feature list for each email
    # rows = emails, columns = words
    bow_mat = np.array(bow_mat_list)

    # return matrix and list of words
    return bow_mat

def make_bow_given_dict_string(input_str,global_bow_words):

    bow_list = []
    msg_word_dict = dict.fromkeys(global_bow_words,0)

    body = input_str
    exclamaions = count_exclamations(body)
    body = replace_newlines(body)
    body = strip_punctuation(delete_nums(body)).lower()
    split_body = body.split(' ')
    for word in split_body:
        if word in msg_word_dict.keys():
            msg_word_dict[word] += 1

    bow_list.append(msg_word_dict)

    bow_mat_list = []
    for entry in bow_list:
        bow_mat_list.append(entry.values())

    bow_mat = np.array(bow_mat_list)

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


def train_bow_classifier(mbox,num_words):

    # split data
    split_pct = 0.6  # test-train split percent
    split = split_by_response(mbox)
    num_pos = len(split[0])
    num_neg = len(split[1])
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

    # # get most common words in pos / neg
    # pos_data = train_pos + test_pos
    # neg_data = train_neg + test_neg
    # pos_bow_mat, global_bow_words_pos = make_bow(pos_data, num_words)
    # print global_bow_words_pos
    # neg_bow_mat, global_bow_words_neg = make_bow(neg_data, num_words)
    # print global_bow_words_neg

    # return

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
    # train_bool_responses = np.array(train_bool_responses)
    train_times = np.array(train_times)
    # test_bool_responses = np.array(test_bool_responses)
    test_times = np.array(test_times)
    train_bool_responses = np.array(train_labels)
    test_bool_responses = np.array(test_labels)

    classifiers = []

    # train, evaluate, and test random forest
    rf_test_scores = []
    k = np.arange(20)+1
    parameters = {'n_estimators': k}
    rf = RandomForestClassifier()
    print 'starting grid search'
    rf = sklearn.grid_search.GridSearchCV(rf, parameters, cv=10)
    rf.fit(train_bow_mat,train_bool_responses)
    rf_test_scores.append(rf.score(test_bow_mat,test_bool_responses))
    print 'rf trained'

    # train, evaluate, and test SVM
    c = [1,10] #,100,1000]
    parameters = {'C': c}
    svm_test_scores = []
    # svm = SVC(kernel='linear', probability=False)
    svm = SVC(C=1.0,kernel='linear', probability=False)
    print 'starting grid search'
    # svm = sklearn.grid_search.GridSearchCV(svm, parameters, cv=10)
    svm.fit(train_bow_mat,train_bool_responses)
    svm_test_scores.append(svm.score(test_bow_mat,test_bool_responses))
    print 'svm trained'

    # print test scores
    print rf_test_scores
    print svm_test_scores

    classifiers.append(rf)
    classifiers.append(svm)

    return classifiers, global_bow_words


def evaluate_bow_classifiers(classifiers,global_bow_words,input_message):
    
    # transform input message to matrix
    input_bow_mat = make_bow_given_dict_string(input_message, global_bow_words)

    for classifier in classifiers:
        print classifier.predict(input_bow_mat)


def run_all(mbox,num_words):

    input_message = "hey all i hope you're doing well. please respond to this message at your earliest convenience. scas scas scas scas respond respond respond willy anna long message here please respond respond asap asap asap asap asap why aren't you responding responses give me more data to crunch this classifier really doesn't seem to like short messages don't know what's going on please respond respond respond respond scas scas money budget budget budget hungry harvard me you you you you email office have at with a in you and of to the the to and of you a in in for scas is this be on if with will are do by director director by do more know harvard our our our important urgent board summer committee questions clients great court them room mailing information dont pbh free pbh hi when small time one hey come would hours people questions service its its its comp comp comp when legal interest guys school join join mail boston message"

    classifiers, global_bow_words = train_bow_classifier(mbox,num_words)
    evaluate_bow_classifiers(classifiers,global_bow_words,input_message)
