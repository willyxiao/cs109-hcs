import mrjob

def mapfn(k, v):
  import mailbox
  import email.utils
  import time
  import datetime

  mbox = mailbox.mbox(v)
  for msg in mbox:
    try:
      email_date = datetime.datetime.fromtimestamp(time.mktime(email.utils.parsedate(msg['Date'])))
      yield email_date.year, k
    except:
      yield None, 1

def reducefn(k, vs):
  uniq_lists = set()
  for v in vs:
    uniq_lists.add(v)
  return len(uniq_lists)

if __name__ == '__main__':
  job = mrjob.MrJob(mapfn, reducefn, name="dayhour", test=False)
  print job.run()
