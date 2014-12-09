import mrjob

def mapfn(k, v):
  import re
  import mailbox
  pattern = "^(\[.+\]|\s|Re:|Fwd:)+"

  mbox = mailbox.mbox(v)
  subjects = set()
  for msg in mbox:
    try:
      subject = re.sub("\W", "", re.sub(pattern, "", msg['Subject'])).lower()
      yield subject, 1
    except:
      yield None, 1

def reducefn(k, vs):
  return sum(vs)

if __name__ == '__main__':
  job = mrjob.MrJob(mapfn, reducefn, name="nsubjects", test=False)
  print job.run()
