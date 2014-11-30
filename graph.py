import mrjob

def mapfn(k, v):
  import mbox_to_graph
  import json

  try:
    outfile = open("out/file" + str(k), "w")
    json.dump(mbox_to_graph.make_graph(v), outfile)
    outfile.close()
  except:
    logging.error("Failed on " + v)

def reducefn(k, vs):
  return vs

if __name__ == '__main__':
  job = mrjob.MrJob(mapfn, reducefn, name="graph", test=True)
  print job.run()
