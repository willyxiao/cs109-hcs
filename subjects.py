import mrjob

def mapfn(k, v):
  import re
  import mailbox
  pattern = "^(\[.+\]|\s|Re:|Fwd:)+"

  mbox = mailbox.mbox(v)
  for msg in mbox:
    yield re.sub(pattern, "", msg['Subject']), 1

def reducefn(k, vs):
  return sum(vs)

if __name__ == '__main__':
  job = mrjob.MrJob(mapfn, reducefn, name="subjects", test=False)
  print job.run()
