import mincemeat
import glob
import logging
import os
import sys
import time
import paramiko

class MrJob:
  password = "hello"
  server_ip = "10.102.75.2"
  client_ips = ["10.102.75.4", "10.102.75.6", "10.102.75.8"]

  def __init__(self, mapfn, reducefn, test=False):
    self.mapfn = mapfn
    self.reducefn = reducefn

    glob_prefix = "/mnt"
    glob_suffix = "*.mbox"
    glob_body = "subset" if sample else "archives"
    glob_str = [glob_prefix, glob_body, glob_suffix].join("/")

    self.data = dict(enumerate(glob.glob(glob_str)))

  def run(self):
    if os.fork() == 0:
      time.sleep(5)
      self.start_clients()
      sys.exit()
    else:
      self.results = self.start_server()
      return self.results

  def start_clients(self):
    for ip in client_ips:
      self.start_client(ip)

  def start_client(self, ip):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
    client.connect(ip, username="root")
    stdin, stdout, stderr = client.exec_command('mincemeat.py -p ' + password + ' 10.102.75.2')
    client.close()

  def start_server(self):
    logname = "mrjob" + str(int(time.time())) ".log"
    logging.basicConfig(filename=logname,level=logging.DEBUG)

    s = mincemeat.Server()
    s.datasource = self.data
    s.mapfn = self.mapfn
    s.reducefn = self.reducefn
    return s.run_server(password=password)


