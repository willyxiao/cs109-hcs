#!/bin/python

import mbox_to_bow
import mbox_to_ngram
import pickle
import sys
import json

# Load classifiers and dictionaries
bow_classifiers = pickle.load(open('bow_classifiers.p','rb'))
ngram_classifiers = pickle.load(open('ngram_classifiers.p','rb'))
global_bow_words = pickle.load(open('global_bow_words.p','rb'))
global_ngram_words = pickle.load(open('global_ngram_words.p','rb'))

# Get default input message...
# input_message = "hey all i hope you're doing well. please respond to this message at your earliest convenience. scas scas scas scas respond respond respond willy anna long message here please respond respond asap asap asap asap asap why aren't you responding responses give me more data to crunch this classifier really doesn't seem to like short messages don't know what's going on please respond respond respond respond scas scas money budget budget budget hungry harvard me you you you you email office have at with a in you and of to the the to and of you a in in for scas is this be on if with will are do by director director by do more know harvard our our our important urgent board summer committee questions clients great court them room mailing information dont pbh free pbh hi when small time one hey come would hours people questions service its its its comp comp comp when legal interest guys school join join mail boston message"
input_message = sys.argv[1]

# Function to predict
def predict_message(message):
	bow_message = mbox_to_bow.make_bow_given_dict_string(message,global_bow_words)
	ngram_message = mbox_to_ngram.make_ngram_given_dict_string(message,global_ngram_words,1)

	predictions = {'bow':[],'ngram':[]}

	for classifier in bow_classifiers:
		predictions['bow'].extend(classifier.predict(bow_message))

	for classifier in ngram_classifiers:
		predictions['ngram'].extend(classifier.predict(ngram_message))
		# print classifier.predict(ngram_message)

	print json.dumps(predictions)


# MAIN
if __name__ == '__main__':
	predict_message(input_message)
