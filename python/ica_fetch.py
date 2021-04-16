#!/usr/bin/python3

# This Python program fetches the intermedite certificates excluding the server and RootCA cert) 
# from a list of servers. It stores them in a list and prints the list and the number of distinct 
# intermediate CA certs. 

# Run as 
#  python3 ica_fetching.py ../data/example100.json --server_file ../data/umbrella-top-1m.csv_4-5-2021.csv --num_servers 100 --line_start 10
# or to just update the empty ICAs in the JSON file 
# python3 ica_fetching.py ../data/example2.json --num_servers 100 --line_start 10

import sys, os.path
import socket
from OpenSSL import SSL 
import json, csv
import argparse
from pprint import pprint

PROGRESS_PRINT_CTR = 10 # To be used to print progress dots as the ICAs are being fetched.
WRITE_CTR = 100 # To be used to write to file periodically so we don't lose data in case of failure.

def get_certificate_chain(host):
    """
    Extracts the certificate chain from the provided host.
    params:
        host (str): hostname
    output:
        -list of ICA certificates (not leaf or root CA) in the chain 
        -in case of exception (eg. timeout) returns -1
    """
    try:
      socket.gethostbyname(host)
    except: 
      #print("=======", end ="", flush=True)
      return []

    ica_certs_list = list()
    try:
        # Use Sockets and SSL to connect to the server to fetch the required certs 
        dst = (host, 443)
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        #timeout = socket.getdefaulttimeout()
        #print("System has default timeout of {} for create_connection".format(timeout))
        sock = socket.create_connection(dst,timeout=1.0) # 2 seconds to not block too long in case of connection error
        s = SSL.Connection(ctx, sock)
        sock.settimeout(None) # Bring back to blocking because it returns without any certs
        s.set_connect_state()
        s.set_tlsext_host_name(dst[0].encode())
        s.sendall('QUIT\n\n')
        # s.recv(16)
        leaf_cert = s.get_peer_certificate() # fetch the server cert
        cert_chain = s.get_peer_cert_chain() # fetch the cert chain (includes server cert and root)
        for ic in cert_chain: # for each cert in the chain
           # if     it is not the server leaf cert          or  a root CA cert
           #print(" --",ic.get_subject(),"+",ic.get_issuer())
           if (leaf_cert.get_subject() != ic.get_subject() and ic.get_subject()!=ic.get_issuer()): 
             #print("  --",ic.get_subject())
             ica_certs_list.append(ic) # add it to the Itermediate CA list
        #print("+", end="",flush=True)
        return ica_certs_list
    except: 
        #print("-", end="",flush=True)
        return [] # Return empty list if something went wrong and we didn't get anything back

paramparser = argparse.ArgumentParser(description='Fetch ICAs for a list of servers and store in JSON format.')
paramparser.add_argument('server_ICA_file', 
			help="JSON file to store the servers and their ICAs.")
paramparser.add_argument('--server_file', nargs='?',
			help="File containing the servers. If empty, we will only update the server_ICA_file JSON objects for the servers that had no ICA information stored for them.")
paramparser.add_argument("--num_servers", type=int, nargs='?', default=1000000,
			help="Number of servers to fetch ICAs for. Default is 1M.")
paramparser.add_argument("--line_start", type=int, nargs='?', default=1,
			help="Starting line for server to start fetching ICAs for. Default is 1.")
args = paramparser.parse_args()

'''# Pring input arguments for testing 
print(args.server_ICA_file)
print(args.num_servers)
print(args.server_file)
print(args.line_start)
'''

def ica_list_to_json(ica_certs):
  json_s=""
  for cert in ica_certs: 
      tmp = "".join("/{0:s}={1:s}".format(name.decode(), value.decode()) for name, value in cert.get_subject().get_components()) 
      json_s += """ { "Subject": \"""" + tmp + """\", """
      tmp = str(cert.subject_name_hash())
      json_s += """ "SubjDigest": \"""" + tmp + """\", """
      tmp = "".join("/{0:s}={1:s}".format(name.decode(), value.decode()) for name, value in cert.get_issuer().get_components())
      json_s += """ "Issuer": \"""" + tmp + """\", """ 
      tmp = str(cert.digest("sha256"))
      json_s += """ "CertDigest": \"""" + tmp + """\"},"""
  return json_s[:len(json_s)-1] # Remove uncessary comma that would break json

# Starting 
srv_cnt = args.num_servers # counter for the number of server to fetch ICAs for
if args.server_file: # If passed as input parameter, parse the servers file and fetch ICAs
  print ("Fetching ICAs for", args.num_servers, "servers...")
  sfile = args.server_file # the file that contains the servers. 
  json_str = "["; 
  if not os.path.isfile(sfile): 
      print('File does not exist.') # Throw error if the file does not exist.
  else:
    with open(sfile) as csv_file: # Open and read the file with the servers.
        csv_reader = csv.reader(csv_file, delimiter=',')
        jsonFile = open(args.server_ICA_file, "w").close() # Start with empty file. TODO: Need to throw error if it already exists.
        for row in csv_reader: 
            if (int(row[0]) % PROGRESS_PRINT_CTR == 0): # For every PROGRESS_PRINT_CTR servers
              print(".", end ="", flush=True) # print progress dot 
            if int(row[0]) - args.line_start > srv_cnt-1: # Exit it you processed the number of servers required
               break
            if (not int(row[0]) < args.line_start): # Only start fetching ICAs at the server line passed in. 
               #print(row[0], end ="-", flush=True) # print progress dot 
               json_str += """ {"Id": \"""" + row[0] +"""\", """
               json_str += """ "Server": \"""" + row[1] +"""\", """
               #print("server:", row[1], end =", ", flush=True)
               certs = get_certificate_chain(row[1]) # Fetch the ICA cert chain from the server
               #pprint(certs)
               #print("--", len(certs))
               json_str += """ "ICAS": [""" + ica_list_to_json(certs) + """] },"""
            #if int(row[0]) < srv_cnt: # If it is the last entry, don't add comma in the json
            #  json_str += json_str + ","
              #TODO: If certs are empty, then increase srv_cnt++ to get one more entry because this was a fluke.
               if ((int(row[0]) % WRITE_CTR == 0) and (int(row[0]) - args.line_start < srv_cnt-1)): # For every PROGRESS_PRINT_CTR servers, write to file. We don't write to file in the last iteration, because we will use it to remove the last comma to not break json and then write to the json file
                   jsonFile = open(args.server_ICA_file, "a")
                   jsonFile.write(json_str)
                   jsonFile.close()
                   json_str = ""
  json_str = json_str[:len(json_str)-1] + "]" # Remove uncessary comma that would break json
  jsonFile = open(args.server_ICA_file, "a")
  jsonFile.write(json_str)
  jsonFile.close()

else: # if only asked to populate the server json, only parse the server entries in the JSON file without any ICAs 
  print ("Populating empty ICA lists in JSON file...")
  ## TODO: Was giving errors at some point, not sure why.  missing ICAs
  jsonFile = open(args.server_ICA_file, "r") # Open the JSON file for reading
  data = json.load(jsonFile) # Read the JSON into the buffer
  data_orig_len = len(data) # Read the JSON into the buffer
  jsonFile.close() # Close the JSON file
  updatedf = 0; 
  for sobj in data: 
    if int(sobj["Id"]) - args.line_start > srv_cnt-1: # Exit it you processed the number of servers required
      break
    if (not int(sobj["Id"]) < args.line_start): # Only start fetching ICAs at the server line passed in.
      for attr, value in sobj.items():
        #print(attr, value)
        #print("++", sobj["ICAS"]) 
        if attr == 'ICAS' and value == []:
          print(sobj['Id']+"."+sobj['Server'], end ="-", flush=True) 
          certs = get_certificate_chain(sobj['Server']) # Fetch the ICA cert chain from the server
          if not certs == []: 
            for i in range(len(certs)): 
              sobj["ICAS"] = [ json.loads(ica_list_to_json(certs)) ]
            print("U.", end =" ", flush=True) 
            updatedf+=1
          else: 
            print("N.", end =" ", flush=True)
      #print(sobj) 

  if updatedf>0:   # Write only if we got more ICAs
    print("== Updated", updatedf, "entries. ==") 
    ## Save our changes to JSON file  
    jsonFile = open(args.server_ICA_file, "w")
    jsonFile.write(json.dumps(data))
    jsonFile.close()
  else: 
    print("== No entries updated. ==")  

