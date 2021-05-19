#!/usr/bin/python3

# Run as 
#  python3 ica_analysis.py ../data/censys.io/example_umbrella1M.json --top 100 --csv --verbose
#  python3 ica_analysis.py ../data/censys.io/example_alexa1M.json --top 100 --csv --verbose

import json
import argparse

#TODO: Clean up functions, names and unused ones. 

# Just to check if a domain occurs twice but in non back to back entries
def update_set(s, t):
  if t in s: 
    return 0
  else: 
    #print("Adding ", t, len(s))
    s.add(t)
    return 1

# Prints list objects in separate lines 
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
  total_cntr = 0
  ss_cert_cntr = 0
  ss_cert_seen_1st_cntr = 0 
  empty_subject_dn_cntr = 0
  server_cert_cntr = 0 

  server_set = set() 
  ica_dict = {}
  ica_set = set() # List with distinct ICA certificates

  for line in lines: 
    jobj = json.loads(line)

    if args.verbose and not args.csv: 
      if (int(jobj['alexa_rank']) % PROGRESS_PRINT_MODULO == 0): # For every PROGRESS_PRINT_MODULO servers
        print(".", end ="", flush=True) # print progress dot 

    if not 'is_ca' in jobj: # TODO: Here we could add a check with for CA: True so we disregard no CA certs.
      server_cert_cntr += 1
      #print(jobj['domain'])
      if update_set(server_set, jobj['domain']): 
        ica_dict[jobj['domain']] = 0
      #print(jobj['domain'])
    elif not jobj['is_ca']: # TODO: Here we could add a check with for CA: True so we disregard no CA certs.
      #print(jobj['domain'])
      server_cert_cntr += 1
      if update_set(server_set, jobj['domain']): 
        ica_dict[jobj['domain']] = 0

    elif not 'subject_dn' in jobj: # TODO: Here we need to address the lack of subject_dn, or maybe just count the errors. 
      empty_subject_dn_cntr += 1 
      if update_set(server_set, jobj['domain']): 
        ica_dict[jobj['domain']] = 0

    elif jobj['subject_dn'] == jobj['issuer_dn']:  # If Root CA / self-signed we won't cache it, just count it, it should not be sent in TLS.
      ss_cert_cntr += 1 
      # Just to check if a domain occurs twice but in non back to back entries
      if update_set(server_set, jobj['domain']): 
        ica_dict[jobj['domain']] = 0
        ss_cert_seen_1st_cntr += 1
            
    else:  # If we are dealing with an ICA 
      update_set(ica_set, jobj['fingerprint_sha256']) # Add ICA Subject to the distinct ICA list #TODO: Here put in subject_dn
 
      #if jobj['subject_dn'] == 'C=US, ST=New Jersey, L=Jersey City, O=The USERTRUST Network, CN=USERTrust RSA Certification Authority': #TODO: Delete
      #  print("===Skata-", jobj['subject_dn'], "-", jobj['issuer_dn'],"-", jobj['subject_dn'] == jobj['issuer_dn'])

      # Just to check if a domain occurs twice but in non back to back entries
      if not update_set(server_set, jobj['domain']): 
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
  num_icas_cntrs = list(range(5)) 
  for i in range(5):
    num_icas_cntrs[i]=0

  # Adding up ICA counters
  for s in server_set: 
    #if ica_dict[s] == 2: #Only for troubleshooting
    #  print(s) 
    if ica_dict[s] > 3: 
      num_icas_cntrs[4] += 1 # increase the >3 ICAs counter
    else: 
      #if num_icas==3: # Print servers based on ICA size, only for troublshooting.
      #  print("Server", prev_domain, "had", num_icas ,"ICAs.", end=" ",flush=True)
      num_icas_cntrs[ica_dict[s]] += 1 # increase 1-3 ICAs counter

  if not args.csv: 
    print("") # print empty line.
    print("Servers with 0 ICAs:", num_icas_cntrs[0] , ", 1 ICA:", num_icas_cntrs[1], ", 2 ICAs:", num_icas_cntrs[2], 
          ", 3 ICAs:", num_icas_cntrs[3], ", >3 ICAs:", num_icas_cntrs[4], ", Total Servers:", len(server_set), 
          # "=", num_icas_cntrs[0]+num_icas_cntrs[1]+num_icas_cntrs[2]+num_icas_cntrs[3]+num_icas_cntrs[4], 
          # "-", rootCA_seen_1st,
          )
    print("Self-signed certs:", ss_cert_cntr, ", non-CA certs:", server_cert_cntr, ", Certs w/o Subject DN:", empty_subject_dn_cntr)
    print("Distinct ICA certs:", len(ica_set)) 

  # Print statistics in CSV format [0 ICAs, 1 ICA, 2 ICAs, 3 ICAs, >3 ICAs, # distinct servers, Self-signed certs, non-CA certs, Certs w/o Subject, Distinct ICAs]
  else: 
    #print("0 ICAs, 1 ICA, 2 ICAs, 3 ICAs, >3 ICAs, # distinct servers, Self-signed certs, non-CA certs, Certs w/o Subject, Distinct ICAs")
    print(args.ICA_JSON_file, ",", num_icas_cntrs[0], ",", num_icas_cntrs[1], ",", num_icas_cntrs[2], 
          ",", num_icas_cntrs[3], ",", num_icas_cntrs[4], ",", len(server_set), 
          ",", ss_cert_cntr, ",", server_cert_cntr, ",", empty_subject_dn_cntr, 
          ",",len(ica_set)
          )
  #print_list(ica_set)

  if args.verbose and not args.csv: 
    # Now let's confirm the ICAs we got are correct 
    error = 0
    cntr = 0
    for line in lines: 
      jobj = json.loads(line)
      cntr += 1 
      if not 'subject_dn' in jobj: # If no subject_dn, the cert should not have been in the ica_set
        pass 
      elif not jobj['fingerprint_sha256'] in ica_set: # If the cert is not in the ica_set
        if not 'is_ca' in jobj:  # it either does not have a BasicContraint CA: True/False
          pass
        elif not jobj['is_ca']:  # or is a leaf, non-CA cert with BasicContraint CA: False
          pass 
        elif jobj['subject_dn'] == jobj['issuer_dn']: # or is a Root / self-signed cert
          pass 
        else:  # Othewise it is an ICA cert, and should be in the ica_set
          error = 1
          break
      else: # If the cert is in the ica_set jobj['subject_dn'] in ica_set
        if not 'is_ca' in jobj:  # if it does not have a BasicContraint CA: True/False, then it should not have been in the ica_set
          error = 1
          break
        elif not jobj['is_ca']:  # if it is a leaf / non-CA cert with BasicContraint CA: False, then it should not have been in the ica_set
          error = 1
          break
        elif jobj['subject_dn'] == jobj['issuer_dn']: # or is a Root / self-signed cert
          error = 1
          break
        else:  # Othewise it is an ICA cert (unless it was a Root self-signed cert which we are not checking), and should be in the ica_set
          pass
      if cntr>srv_cnt-1: 
        break
    if error:
      print("Something went wrong with the ICA set.")
    else: 
      print("Checked all certs again. ICA set was right.")

  #print_list(ica_set)
