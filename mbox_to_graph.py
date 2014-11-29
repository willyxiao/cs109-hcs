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
      if A_email not in graph:
        graph[A_email] = {}

      if B_email not in graph[A_email]:
        graph[A_email][B_email] = new_graph_weight(A_time - B_time)
      else:
        graph[A_email][B_email] = update_graph_weight(graph[A_email][B_email], A_time - B_time)

    mailing_threads[thread].append((A_email, A_time))

  return graph

def new_graph_weight(timedelta):
  diff = timedelta.total_seconds()
  if diff < 1:
    logging.error("Time difference less than 1")
    diff = 1
  return 1/math.sqrt(diff)

def update_graph_weight(old_weight, new_timedelta):
  return old_weight + new_graph_weight(new_timedelta)
