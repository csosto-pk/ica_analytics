#!/usr/bin/python3

# Run python3 topumbrella-alexa1m-comparison.py ../data/censys.io/example_umbrella1M.json ../data/censys.io/example_alexa1M.json --top 10


import os.path
import argparse
import json
from ica_analysis import update_set 

PROGRESS_PRINT_cntr = 1000 # To be used to print progress dots as the ICAs are being processed.

# Read JSON file into lines 
def read_file(jf):
  if not os.path.isfile(jf):  
    print('File does not exist.') # Throw error if the file does not exist.
    return None 
  else:
    file = open(jf, 'r')
    lines = file.readlines()
    file.close()
    return lines 

# Returns the server domains cert and the server domain dictionary with the Alexa/Umbrella ranking as the value.
def get_server_rankings_from_file(jf, cntr):
  server_set = set() 
  f_server_dict = {}
  lines = read_file(jf) 
  if not lines == None: 
    for line in lines: 
      jobj = json.loads(line)

      if update_set(server_set, jobj['domain']): # If it is the first time we see the server
        if 'alexa_rank' in jobj:  # If it Alexa
          f_server_dict[jobj['domain']] = jobj['alexa_rank'] # Add the Alexa ranking in the server dictionary 
          if (int(jobj['alexa_rank']) % PROGRESS_PRINT_cntr == 0): # For every PROGRESS_PRINT_cntr servers
            print(".", end ="", flush=True) # print progress dot
        else:  # If it is Umbrella
          f_server_dict[jobj['domain']] = jobj['umbrella_rank'] # Add the Umbrella  ranking in the server dictionary 
          if (int(jobj['umbrella_rank']) % PROGRESS_PRINT_cntr == 0): # For every PROGRESS_PRINT_cntr servers
            print(".", end ="", flush=True) # print progress dot
      else:  # Otherwise, if we have seen this server before 
        if 'alexa_rank' in jobj: # If it Alexa
          if not f_server_dict[jobj['domain']] == jobj['alexa_rank']: # Alert that two ranking for that server differed
            print("Server", jobj['domain'], "had entries with different Alexa rankings in the dataset. ")
            break # And Exit
        else: # If it is Umbrella
          if not f_server_dict[jobj['domain']] == jobj['umbrella_rank']: # Alert that two ranking for that server differed
            print("Server", jobj['domain'], "had entries with different Umbrella rankings in the dataset. ")
            break # And Exit
      if len(server_set) == cntr: # Exit when exceeding the maximum server counter
        break 
  print("")
  return server_set, f_server_dict

# Returns the diff of the rankings of the server domains divided by 1000. For a domain the is in one dictionary and not the other it adds 1000000
def server_ranking_distance_metric(sdict1, sdict2): 
  # Always start from the dictionary that has more elements so we don't undercalculate the difference.
  if len(sdict1) > len (sdict2):  
    sd1 = sdict1
    sd2 = sdict2
  else: 
    sd1 = sdict2
    sd2 = sdict1
  metric = 0
  for s in sd1: 
    if (int(sd1[s]) % PROGRESS_PRINT_cntr == 0): # For every PROGRESS_PRINT_cntr servers
      print("@", end ="", flush=True) # print progress dot
    if s in sd2: 
      metric += abs(int(sd1[s])-int(sd2[s]))
    else: 
      metric += 1000000
  print("")
  return metric / 1000


# Returns the % of server difference of the servers domain in the two dictionaries
def server_server_diff_metric(sdict1, sdict2): 
  # Always start from the dictionary that has more elements so we don't undercalculate the difference.
  if len(sdict1) > len (sdict2):  
    sd1 = sdict1
    sd2 = sdict2
  else: 
    sd1 = sdict2
    sd2 = sdict1
  metric = 0
  for s in sd1: 
    if (int(sd1[s]) % PROGRESS_PRINT_cntr == 0): # For every PROGRESS_PRINT_cntr servers
      print("*", end ="", flush=True) # print progress dot
    if s not in sd2: 
      metric += 1
  print("")
  return metric / len(sd1)



if __name__ == "__main__":

  paramparser = argparse.ArgumentParser(description='Analyze and Comprate TopX server datasets.')
  paramparser.add_argument('f1', 
                           help="TopX First File")
  paramparser.add_argument('f2',
                           help="TopX Second File")
  paramparser.add_argument("--top", type=int, nargs='?', default=1000000,
                           help="Number of servers to fetch ICAs for. Default is 1M.")
  args = paramparser.parse_args()

  '''# Pring input arguments for testing 
  print(args.f1)
  print(args.f2)
  print(args.top)'''

  # Starting 
  #print ("Comparing", args.f1, "and", args.f2, "datasets.")

  max_srv = args.top # counter for the number of server to fetch ICAs for
  jf1 = args.f1 # the first file that contains the servers
  jf2 = args.f2 # the second file that contains the servers

  #flines = read_file(jf1)

  f1_server_set, f1_server_dict = get_server_rankings_from_file(jf1, max_srv)
  #print(f1_server_set)
  #print(f1_server_dict)
  f2_server_set, f2_server_dict = get_server_rankings_from_file(jf2, max_srv)
  #print(f2_server_set)
  #print(f2_server_dict)


  print("Alexa-Alexa, Umbrella-Umbrella simple server diff % metrics (should be 0): ", server_server_diff_metric(f1_server_dict, f1_server_dict),
        ",", server_server_diff_metric(f2_server_dict, f2_server_dict))
  print("Alexa-Umbrella simple server diff % metric: ", server_server_diff_metric(f1_server_dict, f2_server_dict))
  print("Umbrella-Alexa simple server diff % metric: ", server_server_diff_metric(f2_server_dict, f1_server_dict))

  print("Alexa-Alexa, Umbrella-Umbrella ranking diff metrics (should be 0): ", server_ranking_distance_metric(f1_server_dict, f1_server_dict),
        ",", server_ranking_distance_metric(f2_server_dict, f2_server_dict))
  print("Alexa-Umbrella ranking diff metric: ", server_ranking_distance_metric(f1_server_dict, f2_server_dict))
  print("Umbrella-Alexa ranking diff metric: ", server_ranking_distance_metric(f2_server_dict, f1_server_dict))

