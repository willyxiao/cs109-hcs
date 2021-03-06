#! /usr/bin/env python
import json
import mbox_to_graph
import sys

inpath = "/mnt/archives/"

outpath = "webpage/"

# takes the name of the list (i.e. without the '/mnt/archives/')
def create_json(mlist, year):
  full_path = inpath + mlist + ".mbox"
  data = mbox_to_graph.make_graph(full_path, year)
  with open(outpath + "{0}-{1}.json".format(mlist, year), "w") as outfile:
    json.dump(data, outfile)

if __name__ == "__main__":
  if (len(sys.argv) < 3):
    print "Usage: {0} <list> <year>".format(sys.argv[0])
    sys.exit(1)

  create_json(sys.argv[1], sys.argv[2])
