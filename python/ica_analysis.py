#!/usr/bin/python3

# This program process the Censys.io Alexa and Umbrella JSON files and returns statistics on server domains and 
# the certificate chains they return. 

# It takes one files as input. That is the Alexa or Umbrella JSON file extracted from Censys.io based on the 
# Top1M Alexa sites or the Top1M Cisco Umbrella sites on a specific date. The file contains the Alexa 
# alexa_rank or the Umbrella cisco_rank of each server along with the certificates it returned in its 
# TLS certificate chain. 

# It returns the 
#   - File name 
#   - # of servers with 0 ICAs 
#   - of servers with 1 ICA 
#   - of servers with 2 ICAs 
#   - of servers with 3 ICAs 
#   - of servers with >3 ICAs 
#   - # of distinct servers seen 
#   - # self-signed certs seen
#   - # of non-CA/leaf certs seen
#   - # of certs w/o Subject_DN seen
#   - # of distinct ICAs seen (that would need to be cached)

# Run as 
#  python3 ica_analysis.py ../data/censys.io/example_umbrella1M.json --top 100 --csv --verbose
#  python3 ica_analysis.py ../data/censys.io/example_alexa1M.json --top 100 --csv --verbose

import json
import argparse

# Adds t to set s only if it does not exist and return 1. 
# If it exists, it returns 0. 
def update_set(s, t):
  if t in s: 
    return 0
  else: 
    s.add(t)
    return 1

# Prints objects in list in separate lines 
def print_list(c_list): 
  for c in c_list:
     print(c)



if __name__ == "__main__":

  PROGRESS_PRINT_MODULO = 1000 # To be used to print progress dots as the ICAs are being processed.

  paramparser = argparse.ArgumentParser(description='Process ICA statistics from JSON file.')
  paramparser.add_argument('ICA_JSON_file', 
			help="JSON file that includes the servers and their ICAs.")
  paramparser.add_argument("--top", type=int, nargs='?', default=1000000, # Process only the top # of servers in the file.
			help="Number of entries in the JSON file to process. Default is 1M.")
  paramparser.add_argument("--csv", action='store_true', 
			help="CSV statistics output.")
  paramparser.add_argument("--verbose", action='store_true', 
			help="Verbose output")
  #paramparser.add_argument("--line_start", type=int, nargs='?', default=1,
  #			help="Starting entry in the JSON file to process from. Default is 1.")
  args = paramparser.parse_args()

  '''# Pring input arguments for testing 
  print(args.ICA_JSON_file)
  print(args.top)
  print(args.csv)
  '''

  # Read lines from file in order to process them 
  file = open(args.ICA_JSON_file, 'r')
  lines = file.readlines()
  file.close()

  srv_cnt = args.top # counter for the number of server entries to process.
  ss_cert_cntr = 0 # Self-signed certficates counter
  ss_cert_seen_1st_cntr = 0  # Counter for self-signed certficates seen first in the certificate chain (considered abnormal)
  empty_subject_dn_cntr = 0 # Counter for certificates that have no subject_dn set (considered abnormal)
  server_cert_cntr = 0 # counter for server domains processed

  server_set = set() # Set of processed server domains
  ica_dict = {}  # dictionary the includes the server domain as key and the number of ICAs it provided in its cert chain
  ica_set = set() # List with distinct ICA certificates

  for line in lines: 
    jobj = json.loads(line) # Get each JSON line from the dataset

    if args.verbose and not args.csv: # Print progress dots if we are not get CSV output
      if (int(jobj['alexa_rank']) % PROGRESS_PRINT_MODULO == 0): # for every PROGRESS_PRINT_MODULO servers
        print(".", end ="", flush=True) 

    if 'cisco_domain' in jobj: # Keep the server domain and ranking depending on the data set
      dmn = jobj['cisco_domain'] # The Umbrella dataset has domain and cisco_domain. Keep that one.
      rnk = int(jobj['cisco_rank']) # The Umbrella dataset has ranking and cisco_rank. Keep that one.
    else: 
      dmn = jobj['domain'] # The Alexa dataset has only domain. 
      rnk = int(jobj['alexa_rank']) # The Umbrella dataset has ranking and alexa_rank. Keep that one.

    if rnk < srv_cnt: # Since data is not in ordered ranking we need to go through the whole set and 
                      # ignore servers ranked higher than maximum server counter
      if not 'is_ca' in jobj: # If BasicConstraints CA: True/False  was not present in the cert then it was a leaf cert, not CA/ICA
        #print(dmn)
        server_cert_cntr += 1  # count the leaf cert
        if update_set(server_set, dmn): # Add the server in the server set so we know we saw that domain.
          ica_dict[dmn] = 0  # If we had not seen the domain before (was not in the server set) then the ica counter 
                             # (ica_dict dictionary value for that domain key) for that domain should start from 0 
                             # because the first cert we just saw was a leaf, and not an ICA cert.
      elif not jobj['is_ca']: # If BasicConstraints CA: False in the cert then it was a leaf cert, not CA/ICA
        #print(dmn)
        server_cert_cntr += 1 # count the leaf cert
        if update_set(server_set, dmn): # Add the server in the server set so we know we saw that domain.
          ica_dict[dmn] = 0  # If we had not seen the domain before (was not in the server set) then the ica counter 
                             # (ica_dict dictionary value for that domain key) for that domain should start from 0 
                             # because the first cert we just saw was a leaf, and not an ICA cert.

      elif not 'subject_dn' in jobj: # If Subject_DN was not present in the cert it is in error, we will not count it. 
        empty_subject_dn_cntr += 1  # increment the empty DN counter
        if update_set(server_set, dmn): 
          ica_dict[dmn] = 0  # If we had not seen the domain before (was not in the server set) then the ica counter 
                             # (ica_dict dictionary value for that domain key) for that domain should start from 0 
                             # because the first cert we just saw was wrong, and not an ICA cert.

      elif jobj['subject_dn'] == jobj['issuer_dn']:  # If Root CA / self-signed we won't cache it, just count it. 
                                                     # It probably should not have not been sent in TLS from the server.
        ss_cert_cntr += 1  # increment the self-signed cert counter
        if update_set(server_set, dmn): # Add the server in the server set so we know we saw that domain. 
          ica_dict[dmn] = 0  # If we had not seen the domain before (was not in the server set) then the ica counter 
                             # (ica_dict dictionary value for that domain key) for that domain should start from 0 
                             # because the first cert we just saw was a self-signed, and not an ICA cert.
          ss_cert_seen_1st_cntr += 1  # count the self-signed certficate seen first in the certificate chain 
            
      else:  # If we are dealing with an ICA certificate 
        update_set(ica_set, jobj['fingerprint_sha256']) # Add the unique certificate SHA256 fingerprint in the ICA Set.
   
        if not update_set(server_set, dmn): # Add the server in the server set so we know we saw that domain. 
          ica_dict[dmn] += 1 # If we had not seen the domain before (was not in the server set) then the ica counter 
                             # (ica_dict dictionary value for that domain key) for that domain should start from 1 
                             # since the first cert we just saw was ICA cert.
        else: 
          ica_dict[dmn] = 1  # Else if we had seen the domain before (was not in the server set) then increment the 
                             # ica counter (ica_dict dictionary value for that domain key) since we just saw one more 
                             # ICA cert.
      #print(ctr, dmn)
      if len(server_set)>srv_cnt-1: # Exit when we find more servers that the maximum server counter. 
        break

  # Now we will process the collected data and provide the statistics. 
  num_icas_cntrs = list(range(5))  # Array that stores number of servers found to have 0, 1, 2, 3, or more ICAs.
  for i in range(5):
    num_icas_cntrs[i] = 0

  # Adding up the ICA counters from the ica_dict dictionary for each unique server in the server_set
  for s in server_set: 
    # print(s) 
    if ica_dict[s] > 3: # If there were more than 3 ICAs for a server 
      num_icas_cntrs[4] += 1 # increment the >3 ICAs counter, since we aggregate all >3ICA to one counter
    else: # otherwise, for ica counters <4
      num_icas_cntrs[ica_dict[s]] += 1 # just increment the separate 1-3 ICAs counter

  # Print detailed information
  if not args.csv: 
    print("") # print empty line.
    print("Servers with 0 ICAs:", num_icas_cntrs[0] , ", 1 ICA:", num_icas_cntrs[1], ", 2 ICAs:", num_icas_cntrs[2], 
          ", 3 ICAs:", num_icas_cntrs[3], ", >3 ICAs:", num_icas_cntrs[4], ", Total Servers:", len(server_set), 
          # "=", num_icas_cntrs[0]+num_icas_cntrs[1]+num_icas_cntrs[2]+num_icas_cntrs[3]+num_icas_cntrs[4], 
          # "Self-signed certs seen 1st in the cert chain: ", ss_cert_seen_1st_cntr,
          )
    print("Self-signed certs:", ss_cert_cntr, ", non-CA certs:", server_cert_cntr, ", Certs w/o Subject DN:", empty_subject_dn_cntr)
    print("Distinct ICA certs:", len(ica_set)) 

  # Print statistics in CSV format [File, 0 ICAs, 1 ICA, 2 ICAs, 3 ICAs, >3 ICAs, # distinct servers, Self-signed certs, non-CA certs, Certs w/o Subject, Distinct ICAs]
  else: 
    #print("File, 0 ICAs, 1 ICA, 2 ICAs, 3 ICAs, >3 ICAs, # distinct servers, Self-signed certs, non-CA certs, Certs w/o Subject, Distinct ICAs")
    print(args.ICA_JSON_file, ",", num_icas_cntrs[0], ",", num_icas_cntrs[1], ",", num_icas_cntrs[2], 
          ",", num_icas_cntrs[3], ",", num_icas_cntrs[4], ",", len(server_set), 
          #",", num_icas_cntrs[0]+num_icas_cntrs[1]+num_icas_cntrs[2]+num_icas_cntrs[3]+num_icas_cntrs[4], 
          ",", ss_cert_cntr, ",", server_cert_cntr, ",", empty_subject_dn_cntr, 
          ",",len(ica_set)
          )
  #print_list(ica_set)

  # If verbose output requested, then run through the collected data as a sanity check to confirm we did not make a mistake.
  if args.verbose and not args.csv: 
    # Now let's confirm the ICAs we got are correct 
    error = 0
    cntr = 0 
    for line in lines: 
      jobj = json.loads(line)  # Get each JSON line from the dataset
      cntr += 1 
      if 'cisco_domain' in jobj: # Keep the ranking depending on the data set
        rnk = int(jobj['cisco_rank']) # The Umbrella dataset has ranking and cisco_rank. Keep that one.
      else: 
        rnk = int(jobj['alexa_rank']) # The Umbrella dataset has ranking and alexa_rank. Keep that one.
      if rnk < srv_cnt: # Since data is not in ordered ranking we need to go through the whole set and 
                        # ignore servers ranked higher than maximum server counter
        if not 'subject_dn' in jobj: # If no subject_dn, the cert should not have been in the ica_set, disregard
          pass 
        elif not jobj['fingerprint_sha256'] in ica_set: # If the cert is not in the ica_set
          if not 'is_ca' in jobj:  # it either does not have a BasicContraint CA: True/False
            pass
          elif not jobj['is_ca']:  # or is a leaf, non-CA cert with BasicContraint CA: False
            pass 
          elif jobj['subject_dn'] == jobj['issuer_dn']: # or is a Root / self-signed cert
            pass 
          else:  # Othewise it is an ICA cert, and should have been in the ica_set
            error = 1
            break
        else: # If the cert is in the ica_set 
          if not 'is_ca' in jobj:  # if it does not have a BasicContraint CA: True/False, then it should not have been in the ica_set
            error = 1
            break
          elif not jobj['is_ca']:  # if it is a leaf / non-CA cert with BasicContraint CA: False, then it should not have been in the ica_set
            error = 1
            break
          elif jobj['subject_dn'] == jobj['issuer_dn']: # if it is a Root / self-signed cert, then it should not have been in the ica_set
            error = 1
            break
          else:  # Othewise it is an ICA cert, and should be in the ica_set
            pass
        if cntr>srv_cnt-1: # Exit when we find more servers that the maximum server counter.
          break

    if error:
      print("Something went wrong with the ICA set.")
    else: 
      print("Checked all certs again. ICA set was right.")

