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

helper_list = set() #TODO: Remove
ica_list = list() # List with distinct ICA certificates
empty_ica_ctr = 0
srv_cnt = args.top # counter for the number of server entries to process.
total_ctr = 0
rootCA_ctr = 0
num_icas_ctrs = list(range(4)) # array that stores number of servers found to have 1, 2, 3, or more ICAs.
for i in range(4):
  num_icas_ctrs[i]=0
prev_domain=''
num_icas = 1
rootCA_seen_1st = 0

for line in lines: 
  jobj = json.loads(line)
  if (int(jobj['alexa_rank']) % PROGRESS_PRINT_CTR == 0): # For every PROGRESS_PRINT_CTR servers
    print(".", end ="", flush=True) # print progress dot 
  if jobj['subject_dn'] == jobj['issuer_dn']:  # If Root CA we won't cache it, just count it, it should not be sent in TLS.
    rootCA_ctr += 1 
    if prev_domain != jobj['domain']: # If the Root CA was seen first we need to not count it in the ICA counter
      num_icas = 0 
      rootCA_seen_1st += 1
      '''
      if num_icas == 1:
         print("+++")
      if num_icas == 2:
         print("---")
      if num_icas == 3:
         print("===")
      if num_icas > 3:
         print("***", jobj['domain'])
      '''
      #print(jobj['domain']) #TODO: Remove
 
      # Just to check if a domain occurs twice but in non back to back entries
      if prev_domain in helper_list: 
        print("OOOOOOOOOps.", prev_domain, jobj['domain'])
      else: 
        helper_list.add(prev_domain)

      #print("===== ",prev_domain, "-", jobj['domain'], num_icas)                                                 
  else:  # If we are dealing with an ICA 
    update_ica_list(ica_list, jobj['subject_dn']) # Add ICA Subject to the distinct ICA list
    if prev_domain == jobj['domain']: # If this is another ICA entry for the server we saw in the last line
      num_icas += 1
      #print("YYY ", num_icas, jobj['domain'],jobj['subject_dn'])
    else:   # If this is another server from the server we saw in the last line
      total_ctr += 1
      #print(jobj['domain']) #TODO: Remove
      
      # Just to check if a domain occurs twice but in non back to back entries
      if prev_domain in helper_list: 
        print("OOOOOOOOOps ", prev_domain, jobj['domain'])
      else: 
        helper_list.add(prev_domain)

      if num_icas==0:
        #print("Server", prev_domain, "had 0 ICAs.", end=" ",flush=True)
        empty_ica_ctr += 1
      elif num_icas>3: 
        #print("Server", prev_domain, "had >3 ICAs.", end=" ",flush=True)
        num_icas_ctrs[3] += 1 # increase the >3 ICAs counter
      else: 
        #if num_icas==3: # Print servers based on ICA size, only for troublshooting.
        #  print("Server", prev_domain, "had", num_icas ,"ICAs.", end=" ",flush=True)
        num_icas_ctrs[num_icas-1]+=1 # increase 1-3 ICAs counter

        #if jobj['domain'] == "picryl.com": #TODO: Remove
        #  print("=.=", num_icas, "-", jobj['domain'])

      num_icas = 1 # And start countring ICAs from 1 since we moved in a new server from the one we saw in the last line
      #print("Server", prev_domain, "-" ,flush=True)
      #print("XXX-", num_icas ,"-", prev_domain, "-", jobj['domain'])
  #print(ctr, jobj['domain'])
  if total_ctr>srv_cnt: #TODO: total_ctr+rootCA_seen_1st ?
    break
  else: 
    prev_domain = jobj['domain']

#if prev_domain == "yoursitedesignhub.com": 
#   print("----", num_icas)
if num_icas==0:
   #print("Server", prev_domain, "had 0 ICAs.", end=" ",flush=True)
   empty_ica_ctr += 1
elif num_icas>3: 
   #print("Server", prev_domain, "had >3 ICAs.", end=" ",flush=True)
   num_icas_ctrs[3] += 1 # increase the >3 ICAs counter
else: 
   #if num_icas==3: # Print servers based on ICA size, only for troublshooting.
   #  print("Server", prev_domain, "had", num_icas ,"ICAs.", end=" ",flush=True)
   num_icas_ctrs[num_icas-1]+=1 # increase 1-3 ICAs counter

print("") # print empty line
print("Servers with 0 ICAs:", empty_ica_ctr , ", 1 ICA:", num_icas_ctrs[0]-1, ", 2 ICAs:", num_icas_ctrs[1], #-1 because we count the stating empty domain as with 1 ICA.
      ", 3 ICAs:", num_icas_ctrs[2], ", >3 ICAs:", num_icas_ctrs[3], ", Total Servers:", total_ctr, 
      "=", empty_ica_ctr+num_icas_ctrs[0]-1+num_icas_ctrs[1]+num_icas_ctrs[2]+num_icas_ctrs[3], 
      "-", rootCA_seen_1st, 
      ", Total+rootCA_seen_1st:", total_ctr+rootCA_seen_1st
      )
print("Root CAs sent unnecessarily:", rootCA_ctr)
#TODO: Check if the distinct CAs are measured properly.
print("Distinct ICA certs:", get_list_cert_count(ica_list)) 

#print_certs_list(ica_list)

