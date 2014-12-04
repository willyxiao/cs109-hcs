import mailbox
import re
import time
import datetime
import email.utils
import pdb
import math
import logging

def make_graph(mbox):
  if type(mbox) is str:
    mbox = mailbox.mbox(mbox)

  pattern = "^(\[.+\]|\s|Re:|Fwd:)+"

  graph = {}
  mailing_threads = {}

  for msg in mbox:
    try:
      thread = re.sub(pattern, "", msg["Subject"])
    except:
      logging.error("Could not parse subject " + str(msg['Subject']))
      continue

    try:
      A_time = datetime.datetime.fromtimestamp(time.mktime(email.utils.parsedate(msg['Date'])))
      A_email = email.utils.parseaddr(msg['From'])[1]
    except:
      logging.error("Could not parse date or email: " + str(msg['Date']) + ", " + msg['From'])
      continue

    if thread not in mailing_threads:
      mailing_threads[thread] = []

    for B_email, B_time in mailing_threads[thread]:
      if A_time > B_time:
        greater_time, lesser_time = A_time, B_time
        greater_email, lesser_email = A_email, B_email
      else:
        greater_time, lesser_time = B_time, A_time
        greater_email, lesser_email = B_email, A_email

      if greater_email not in graph:
        graph[greater_email] = {}

      if lesser_email not in graph[greater_email]:
        graph[greater_email][lesser_email] = new_graph_weight(greater_time - lesser_time)
      else:
        graph[greater_email][lesser_email] = update_graph_weight(graph[greater_email][lesser_email], greater_time - lesser_time)

    mailing_threads[thread].append((A_email, A_time))

  return graph

def new_graph_weight(timedelta):
  diff = timedelta.total_seconds()
  if diff < 1:
    logging.error("Time difference is " + str(diff))
    diff = 1
  return 1/math.sqrt(diff)

def update_graph_weight(old_weight, new_timedelta):
  return old_weight + new_graph_weight(new_timedelta)

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
  print split

  return split

