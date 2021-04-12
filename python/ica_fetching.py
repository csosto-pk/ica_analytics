#!/usr/bin/python3

# This Python program fetches the intermedite certificates excluding the server and RootCA cert) 
# from a list of servers. It stores them in a list and prints the list and the number of distinct 
# intermediate CA certs. 

# Run as 
#  python3 ica_fetching.py file --num_servers 23 --from_line 1 --server_file ../data/umbrella-top-1m.csv_4-5-2021.csv 


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

# Returns 1 if a certificate exists in a certificate list.
def list_contains_cert(ica_list, crt):
  for ic in ica_list: 
    if crt.digest("sha256") == ic.digest("sha256"):
      return 1
  return 0

# Prints Subject and Issuer information of a cert.
def print_cert(c): 
   print("Subject: CN=", c.get_subject().CN, ", O=", c.get_subject().O, ", C=", c.get_subject().C, 
         "Issuer: CN=", c.get_issuer().CN, ", O=", c.get_issuer().O, ", C=", c.get_issuer().C)

# Prints Subject and Issuer information of the certs in a list. 
def print_certs_list(c_list): 
  for c in c_list:
     print_cert(c)

# Prints number or elements in a list 
def print_list_cert_count(c_list): 
  print("Distinct ICA certs Processing: ", len(c_list))

paramparser = argparse.ArgumentParser(description='Fetch ICAs for a list of servers and store in JSON format.')
paramparser.add_argument('server_ICA_file', 
			help="JSON file to store the servers and their ICAs.")
paramparser.add_argument('--server_file', nargs='?',
			help="File containing the servers. If empty, we will only update the server_ICA_file JSON objects for the servers that had no ICA information stored for them.")
paramparser.add_argument("--num_servers", type=int, nargs='?', default=1000000,
			help="Number of servers to fetch ICAs for. Default is 1M.")
paramparser.add_argument("--from_line", type=int, nargs='?', default=1, 
			help="Starting line in the server_file file to fetch ICAs for. Default is 1. ")
args = paramparser.parse_args()

'''# Pring input arguments for testing 
print(args.server_ICA_file)
print(args.num_servers)
print(args.server_file)
print(args.from_line) 
'''

def update_ica_list(icas, ica_certs):
  for cert in ica_certs: 
    if not list_contains_cert(icas, cert): # if it does not exist in the list 
      icas.append(cert)    # only then add it to it
    '''TODO: Update JSON file
    print("Subject: CN=", c.get_subject().CN, ", O=", c.get_subject().O, ", C=", c.get_subject().C, 
    "Issuer: CN=", c.get_issuer().CN, ", O=", c.get_issuer().O, ", C=", c.get_issuer().C, 
    c.digest("sha256"), 
    c.subject_name_hash() 
    #http://pyopenssl.sourceforge.net/pyOpenSSL.html/openssl-x509.html
    '''


#TODO: Delete 
#dest_list = ["cisco.com", "cisco.com", "google.com", "google.com", "microsoft.com", ]

# Starting 
print ("Fetching ICAs for", args.num_servers, "servers...")

ica_list = list() # List with distinct ICA certificates

rows = args.num_servers # counter for the number of server to fetch ICAs for
if args.server_file: # If passed as input parameter, parse the servers file and fetch ICAs
  sfile = args.server_file # the file that contains the servers. 
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
               #print("server:", row[1], end =", ")
               certs = get_certificate_chain(row[1]) # Fetch the ICA cert chain from the server
               #pprint(certs)
               update_ica_list(ica_list, certs)
               #TODO: If certs are empty, then increase rows++ to get one more entry because this was a fluke. 


else: # if only asked to populate the server json, only parse the server entries without any ICAs 
  jsonFile = open("../data/example.json", "r") # Open the JSON file for reading
  data = json.load(jsonFile) # Read the JSON into the buffer
  jsonFile.close() # Close the JSON file
  for sobj in data: 
      for attr, value in sobj.items():
          # print(attr, value)
          if sobj['ICAS'] == []:
             certs = get_certificate_chain(sobj['server']) # Fetch the ICA cert chain from the server
              # print(curr['Subject'])
          #print(sobj['ICAS'][2])	
      #print(sobj) 
  ## Save our changes to JSON file
  jsonFile = open("../data/example.json", "w")
  jsonFile.write(json.dumps(data))
  jsonFile.close()

print_certs_list(ica_list)
#print_list_cert_count(ica_list)



