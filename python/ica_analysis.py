#!/usr/bin/python3

# Run as 
#  python3 ica_analysis.py ../data/censys.io/certs_cert_chain_alexa1M.json --top 100 --line_start 10

import json
import argparse

PROGRESS_PRINT_CTR = 50 # To be used to print progress dots as the ICAs are being processed.

# Returns 1 if a certificate exists in a certificate list.
def list_contains_cert(ica_list, crt):
  for ic in ica_list: 
    if ic == crt: 
      return 1
  return 0

# Adds ica certificate from ica_certs list in icas list only if they does not already exist in it.
def update_ica_list(icas, new_ica_cert):
    if not list_contains_cert(icas, new_ica_cert): # if it does not exist in the list 
      icas.append(new_ica_cert)    # only then add it to it

      # Just to check if a domain occurs twice but in non back to back entries
def update_server_set(ss, serv):
  if serv in ss: 
    return 0
  else: 
    server_set.add(serv)
    return 1

# Prints Subject and Issuer information of the certs in a list. 
def print_certs_list(c_list): 
  for c in c_list:
     print("ICA Subject",c)

# Prints number or elements in a list 
def get_list_cert_count(c_list): 
  return len(c_list)


paramparser = argparse.ArgumentParser(description='Process ICA statistics from JSON file.')
paramparser.add_argument('ICA_JSON_file', 
			help="JSON file that includes the servers and their ICAs.")
paramparser.add_argument("--top", type=int, nargs='?', default=1000000,
			help="Number of entries in the JSON file to process. Default is 1M.")
paramparser.add_argument("--line_start", type=int, nargs='?', default=1,
			help="Starting entry in the JSON file to process from. Default is 1.")
args = paramparser.parse_args()

'''# Pring input arguments for testing 
print(args.server_ICA_file)
print(args.top)
print(args.server_file)
print(args.line_start)
'''

'''
jsonFile = open(args.ICA_JSON_file, "r") # Open the JSON file for reading
data = json.load(jsonFile) # Read the JSON into the buffer
data_orig_len = len(data) # Read the JSON into the buffer
jsonFile.close() # Close the JSON file
'''
file = open(args.ICA_JSON_file, 'r')
lines = file.readlines()
file.close()

srv_cnt = args.top # counter for the number of server entries to process.
total_ctr = 0
rootCA_ctr = 0
rootCA_seen_1st = 0

server_set = set() 
ica_dict = {}
ica_list = list() # List with distinct ICA certificates

for line in lines: 
  jobj = json.loads(line)
  if (int(jobj['alexa_rank']) % PROGRESS_PRINT_CTR == 0): # For every PROGRESS_PRINT_CTR servers
    print(".", end ="", flush=True) # print progress dot 

  if jobj['subject_dn'] == jobj['issuer_dn']:  # If Root CA we won't cache it, just count it, it should not be sent in TLS.
    rootCA_ctr += 1 

    # Just to check if a domain occurs twice but in non back to back entries
    if update_server_set(server_set, jobj['domain']): 
      ica_dict[jobj['domain']] = 0
      rootCA_seen_1st += 1
                                              
  else:  # If we are dealing with an ICA 
    update_ica_list(ica_list, jobj['subject_dn']) # Add ICA Subject to the distinct ICA list #TODO: Make this a set so I can make sure they are distinct and I can check if it existed already. 

    # Just to check if a domain occurs twice but in non back to back entries
    if not update_server_set(server_set, jobj['domain']): 
      #print("Duplicate out of order entry for", jobj['domain'], ", previous entry:", prev_domain)
      ica_dict[jobj['domain']] += 1 
    else: 
      ica_dict[jobj['domain']] = 1
      #print("Server", prev_domain, "-" ,flush=True)
      #print("XXX-", num_icas ,"-", prev_domain, "-", jobj['domain'])
  #print(ctr, jobj['domain'])
  if len(server_set)>srv_cnt-1: 
    break


# array that stores number of servers found to have 0, 1, 2, 3, or more ICAs.
num_icas_ctrs = list(range(5)) 
for i in range(5):
  num_icas_ctrs[i]=0

# Adding up ICA counters
for s in server_set:  
  if ica_dict[s] > 3: 
    num_icas_ctrs[4] += 1 # increase the >3 ICAs counter
  else: 
    #if num_icas==3: # Print servers based on ICA size, only for troublshooting.
    #  print("Server", prev_domain, "had", num_icas ,"ICAs.", end=" ",flush=True)
    num_icas_ctrs[ica_dict[s]] += 1 # increase 1-3 ICAs counter


print("") # print empty line.
#TODO: Check if the ICAs numbers are counted correctly
print("Servers with 0 ICAs:", num_icas_ctrs[0] , ", 1 ICA:", num_icas_ctrs[1], ", 2 ICAs:", num_icas_ctrs[2], 
      ", 3 ICAs:", num_icas_ctrs[3], ", >3 ICAs:", num_icas_ctrs[4], ", Total Servers:", len(server_set), 
      #"=", num_icas_ctrs[0]+num_icas_ctrs[1]+num_icas_ctrs[2]+num_icas_ctrs[3]+num_icas_ctrs[4], 
      # "-", rootCA_seen_1st,
      )
print("Root CAs sent unnecessarily:", rootCA_ctr)
#TODO: Check if the distinct CAs are measured properly.
print("Distinct ICA certs:", get_list_cert_count(ica_list)) 

#print_certs_list(ica_list)

