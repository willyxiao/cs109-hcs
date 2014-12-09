import mailbox
import re
import time
import datetime
import email.utils
import pdb
import math
import logging

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
