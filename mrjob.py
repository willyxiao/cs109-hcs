import mincemeat
import glob
import logging
import os
import signal
import sys
import time
import pickle
import fabric

class MrJob:
  password = "hello"
  command = "mincemeat.py -p " + password + " 10.102.75.2"
  server_ip = "10.102.75.2"
  client_ips = ["10.102.75.4", "10.102.75.6", "10.102.75.8", "208.43.122.12"]

  def __init__(self, mapfn, reducefn, name=None, test=False):
    self.start_time = time.strftime("%Y%m%d%H%M%S")

    if name is None:
      self.name = "mrjob" + self.start_time
    else:
      self.name = name + self.start_time

    self.mapfn = mapfn
    self.reducefn = reducefn

    glob_prefix = "/mnt"
    glob_suffix = "*.mbox"
    glob_body = "subset" if test else "archives"
    glob_str = "/".join([glob_prefix, glob_body, glob_suffix])

    self.data = dict(enumerate(glob.glob(glob_str)))

  def run(self):
    pid = os.fork()

    if pid == 0:
      time.sleep(5)
      self.start_clients()
    else:
      print "Starting server..."
      self.results = self.start_server()
      os.kill(pid, signal.SIGKILL)
      return self.results

  def start_clients(self):
    fabric.tasks.execute(lambda: fabric.api.run(command), hosts=["root@" + ip for ip in self.client_ips])
    fabric.network.disconnect_all()
#    self.maintain_clients(self.client_ips)

  def mantain_clients(ips):
    while True:
      for ip in ips:
        self.mantain_client(ip)


  # def start_client(self, ip):
  #   client = paramiko.SSHClient()
  #   client.load_system_host_keys()
  #   client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
  #   client.connect(ip, username="root")
  #   stdin, stdout, stderr = client.exec_command("/mnt/bin/mrjobclient")
  #   print stdout.read()
  #   client.close()

  def start_server(self):
    logname = self.name + ".log"
    logging.basicConfig(filename=logname,level=logging.DEBUG)

    outname = self.name + ".out"
    outfile = open(outname, "w")

    s = mincemeat.Server()
    s.datasource = self.data
    s.mapfn = self.mapfn
    s.reducefn = self.reducefn
    result = s.run_server(password=self.password)
    pickle.dump(result, outfile)
    return result
