import json
import mbox_to_graph
import sys

inpath = "/mnt/archive/"

outpath = "webpage/"

# takes the name of the list (i.e. without the '/mnt/archive')
def create_json(mlist):
	full_path = inpath + mlist + ".mbox"
	data = mbox_to_graph.make_graph(full_path)
	with open(outpath + mlist + ".json", "w") as outfile:
		json.dump(data, outfile)

if __name__ == "__main__":
	if (len(sys.argv) < 2):
		print "Usage: {0} <list>".format(sys.argv[0])
		sys.exit(1)

	create_json(sys.argv[1])