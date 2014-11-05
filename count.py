import mrjob

def mapfn(k, v):
  import mailbox
  import email.utils
  import time
  import datetime

  mbox = mailbox.mbox(v)
  for msg in mbox:
    email_date = datetime.datetime.fromtimestamp(time.mktime(email.utils.parsedate(msg['Date'])))
    yield (email_date.weekday(), email_date.hour), 1

def reducefn(k, vs):
  return sum(vs)

if __name__ == '__main__':
  job = mrjob.MrJob(mapfn, reducefn, name="dayhour", test=False)
  print job.run()
