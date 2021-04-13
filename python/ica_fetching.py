#!/usr/bin/python3

# This Python program fetches the intermedite certificates excluding the server and RootCA cert) 
# from a list of servers. It stores them in a list and prints the list and the number of distinct 
# intermediate CA certs. 

# Run as 
#  python3 ica_fetching.py ../data/example2.json --num_servers 5 --server_file ../data/umbrella-top-1m.csv_4-5-2021.csv 
# or to just update the empty ICAs in the JSON file 
# python3 ica_fetching.py ../data/example2.json  


import sys, os.path
import socket
from OpenSSL import SSL 
import json, csv
import argparse
from pprint import pprint

PROGRESS_PRINT_CTR = 10 # To be used to print progress dots as the ICAs are being fetched.

def get_certificate_chain(host):
    """
    Extracts the certificate chain from the provided host.
    params:
        host (str): hostname
    output:
        -list of ICA certificates (not leaf or root CA) in the chain 
        -in case of exception (eg. timeout) returns -1
    """
    ica_certs_list = list()

    try:
        # Use Sockets and SSL to connect to the server to fetch the required certs 
        dst = (host, 443)
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        #timeout = socket.getdefaulttimeout()
        #print("System has default timeout of {} for create_connection".format(timeout))
        sock = socket.create_connection(dst,timeout=2.0) # 2 seconds to not block too long in case of connection error
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
           if (leaf_cert.get_subject() != ic.get_subject() and ic.get_subject()!=ic.get_issuer()): 
             ica_certs_list.append(ic) # add it to the Itermediate CA list
        return ica_certs_list
    except: 
        return [] # Return empty list if something went wrong and we didn't get anything back

paramparser = argparse.ArgumentParser(description='Fetch ICAs for a list of servers and store in JSON format.')
paramparser.add_argument('server_ICA_file', 
			help="JSON file to store the servers and their ICAs.")
paramparser.add_argument('--server_file', nargs='?',
			help="File containing the servers. If empty, we will only update the server_ICA_file JSON objects for the servers that had no ICA information stored for them.")
paramparser.add_argument("--num_servers", type=int, nargs='?', default=1000000,
			help="Number of servers to fetch ICAs for. Default is 1M.")
args = paramparser.parse_args()

'''# Pring input arguments for testing 
print(args.server_ICA_file)
print(args.num_servers)
print(args.server_file)
'''

def ica_list_to_json(ica_certs):
  json_s=""
  for cert in ica_certs: 
      tmp = "".join("/{0:s}={1:s}".format(name.decode(), value.decode()) for name, value in cert.get_subject().get_components()) 
      json_s = """ { "Subject": \"""" + tmp + """\", """
      tmp = str(cert.subject_name_hash())
      json_s += """ "SubjDigest": \"""" + tmp + """\", """
      tmp = "".join("/{0:s}={1:s}".format(name.decode(), value.decode()) for name, value in cert.get_issuer().get_components())
      json_s += """ "Issuer": \"""" + tmp + """\", """ 
      tmp = str(cert.digest("sha256"))
      json_s += """ "CertDigest": \"""" + tmp + """\"},"""
  return json_s[:len(json_s)-1] # Remove uncessary comma that would break json

# Starting 
rows = args.num_servers # counter for the number of server to fetch ICAs for
if args.server_file: # If passed as input parameter, parse the servers file and fetch ICAs
  print ("Fetching ICAs for", args.num_servers, "servers...")
  sfile = args.server_file # the file that contains the servers. 
  json_str = "["; 
  if not os.path.isfile(sfile): 
      print('File does not exist.') # Throw error if the file does not exist.
  else:
    with open(sfile) as csv_file: # Open and read the file with the servers.
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader: 
            if (int(row[0]) % PROGRESS_PRINT_CTR == 0): # For every PROGRESS_PRINT_CTR servers
              print(".", end ="", flush=True) # print progress dot 
            if int(row[0]) > rows: # Exit it you processed the number of servers required
               break
            else: 
               json_str += """ {"Server": \"""" + row[1] +"""\", """
               #print("server:", row[1], end =", ")
               certs = get_certificate_chain(row[1]) # Fetch the ICA cert chain from the server
               #pprint(certs)
               json_str += """ "ICAS": [""" + ica_list_to_json(certs) + """] },"""
            #if int(row[0]) < rows: # If it is the last entry, don't add comma in the json
            #  json_str += json_str + ","
              #TODO: If certs are empty, then increase rows++ to get one more entry because this was a fluke.
  print("") # Print new line
  json_str = json_str[:len(json_str)-1] + "]" # Remove uncessary comma that would break json
  jsonFile = open(args.server_ICA_file, "w")
  jsonFile.write(json_str)
  jsonFile.close()

else: # if only asked to populate the server json, only parse the server entries without any ICAs 
  print ("Populating empty ICA lists in JSON file...")
  jsonFile = open(args.server_ICA_file, "r") # Open the JSON file for reading
  data = json.load(jsonFile) # Read the JSON into the buffer
  jsonFile.close() # Close the JSON file
  for sobj in data: 
      for attr, value in sobj.items():
          #print(attr, value)
          #print("++", sobj["ICAS"]) 
          if attr == 'ICAS' and value == []:
            print(" Missing ICAs for", sobj["Server"], end =",", flush=True) 
            certs = get_certificate_chain(sobj['Server']) # Fetch the ICA cert chain from the server
            if not certs == []: 
              for i in range(len(certs)): 
                sobj["ICAS"] = [  json.loads(ica_list_to_json(certs)) ]
              print(" got updated", end =".", flush=True) 
            else: 
              print(" no luck this time either", end =".", flush=True)
      #print(sobj) 
  ## Save our changes to JSON file  
  print("") # Print new line
  jsonFile = open(args.server_ICA_file, "w")
  jsonFile.write(json.dumps(data))
  jsonFile.close()




