import mincemeat
import glob
import logging

logging.basicConfig(filename='count.log',level=logging.DEBUG)

true_glob = "/mnt/archives/*.mbox"
subset_glob = "/mnt/subset/*.mbox"

data = dict(enumerate(glob.glob(true_glob)))

def mapfn(k, v):
  import mailbox
  import socket
  #mbox = mailbox.mbox(v)

  yield 0, 1#mbox.__len__()

def reducefn(k, vs):
  return k, sum(vs)

s = mincemeat.Server()

s.datasource = data
s.mapfn = mapfn
s.reducefn = reducefn

results = s.run_server(password="hello")

outfile = open('count.out', 'w')

for k, v in results:
  outfile.write(v)

