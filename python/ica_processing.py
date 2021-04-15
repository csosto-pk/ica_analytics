#!/usr/bin/python3

# Run as 
#  python3 ica_processing.py ../data/example100.json --num_servers 100 --line_start 10

import json
import argparse

PROGRESS_PRINT_CTR = 50 # To be used to print progress dots as the ICAs are being processed.

# Returns 1 if a certificate exists in a certificate list.
def list_contains_cert(ica_list, crt):
  for ic in ica_list: 
    if crt['CertDigest'] == ic['CertDigest']:
      return 1
  return 0

# Adds ica certificates from ica_certs list in icas list only if they does not already exist in it.
def update_ica_list(icas, new_ica_certs):
  for cert in new_ica_certs: 
    if not list_contains_cert(icas, cert): # if it does not exist in the list 
      icas.append(cert)    # only then add it to it

# Prints Subject, Issuer, and Digest information of a cert.
def print_cert(c): 
   print("Subject:", c['Subject'], ", Issuer:", c['Issuer'], ", Fingerprint:", c['CertDigest'])

# Prints Subject and Issuer information of the certs in a list. 
def print_certs_list(c_list): 
  for c in c_list:
     print_cert(c)

# Prints number or elements in a list 
def get_list_cert_count(c_list): 
  return len(c_list)


paramparser = argparse.ArgumentParser(description='Process ICA statistics from JSON file.')
paramparser.add_argument('ICA_JSON_file', 
			help="JSON file that includes the servers and their ICAs.")
paramparser.add_argument("--num_servers", type=int, nargs='?', default=1000000,
			help="Number of entries in the JSON file to process. Default is 1M.")
paramparser.add_argument("--line_start", type=int, nargs='?', default=1,
			help="Starting entry in the JSON file to process from. Default is 1.")
args = paramparser.parse_args()

'''# Pring input arguments for testing 
print(args.server_ICA_file)
print(args.num_servers)
print(args.server_file)
print(args.line_start)
'''

ica_list = list() # List with distinct ICA certificates
empty_ica_cntr = 0
srv_cnt = args.num_servers # counter for the number of server entries to process.

jsonFile = open(args.ICA_JSON_file, "r") # Open the JSON file for reading
data = json.load(jsonFile) # Read the JSON into the buffer
data_orig_len = len(data) # Read the JSON into the buffer
jsonFile.close() # Close the JSON file
total_ctr = 1
num_icas_ctrs = list(range(4)) # array that stores number of servers found to have 1, 2, 3, or more ICAs.
for i in range(4):
  num_icas_ctrs[i]=0

for sobj in data: 
  if (int(sobj["Id"]) % PROGRESS_PRINT_CTR == 0): # For every PROGRESS_PRINT_CTR servers
    print(".", end ="", flush=True) # print progress dot 
  if int(sobj["Id"]) - args.line_start > srv_cnt-1: # Exit it you processed the number of servers required
    break
  for attr, value in sobj.items():
    #print(attr, value)
    #print("++", sobj["ICAS"]) 
    if attr == 'ICAS': 
      if value == []: # empty ICA list
        empty_ica_cntr += 1  # increase the empty counter       
      else:
        num_icas = get_list_cert_count(value)
        if num_icas>3: 
          print(sobj["Id"], "3 ICAs", end="",flush=True)
          num_icas_ctrs[3]+=1 # increase the >3ICAs counter
        else: 
          num_icas_ctrs[num_icas-1]+=1 # increase 1-3 ICAs counter
        update_ica_list(ica_list, value)
  total_ctr+=1  # increase the server counter.

print("") # print empty line
print("Server entries processed:", total_ctr-1)
#TODO: Check if we catch one server that has more than one ICAs. Like for www.moviefone.com
print("Servers with 1 ICA:", num_icas_ctrs[0], ", 2 ICAs:", num_icas_ctrs[1], 
      ", 3 ICAs:", num_icas_ctrs[2], ", >3 ICAs:", num_icas_ctrs[3])
#TODO: Check if the distinct CAs are measured properly.
print("Distinct ICA certs:", get_list_cert_count(ica_list))
print("Servers without any ICAs:", empty_ica_cntr)

#print_certs_list(ica_list)
