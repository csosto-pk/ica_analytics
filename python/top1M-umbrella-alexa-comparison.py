#!/usr/bin/python3

# This program parses the Censys.io Alexa and Umbrella JSON files and returns statistics on the differences between 
# the Alexa and Cisco Umbrella datasets. 

# It takes two files as input. These are assumed to be the Alexa and Umbrella JSON files extracted from Censys.io 
# on the same day for more accurate results. 

# The first input file SHOULD contain Alexa rankings. And the second the Umbrella rankings. Otherwise the program 
# will throw an error when trying to parse the "alexa_rank"/"cisco_rank" rankings in the JSON.

# It returns the statistics differences between the files. There are different metrics it calculates: 
#   - the simplest one is the difference of the server domains. It calculates the # servers that exist on one 
#     file but not the other and divides be the sum of the servers in each file. If the input files were the same,  
#     the metric should be calculated to be 0.
#   - another metric is the diff of the rankings of the server domains divided by 1000. For servers that exist 
#     in both files it adds the difference of the ranking of these servers. If a server only exists in one file 
#     it adds a difference of 1,000,000. To lower the metric, it divides it with 1000 in the end. If the input 
#     files were the same, the metric should be calculated to be 0.

# Run as 
#  python3 top1M-umbrella-alexa-comparison.py ../data/censys.io/example_alexa1M.json ../data/censys.io/example_umbrella1M.json --top 10 --csv 


import os.path
import argparse
import json
from ica_analysis import update_set 

# Reads JSON file into lines 
def read_file(jf):
  if not os.path.isfile(jf):  
    print('File does not exist.') # Throw error if the file does not exist.
    return None 
  else:
    file = open(jf, 'r')
    lines = file.readlines()
    file.close()
    return lines 

# Returns the server domains set and the server domain dictionary with the Alexa/Umbrella ranking as the value. 
# Takes the JSON file, the top # of server to process from the file and if the extracted ranking should be Alexa 
# or Umbrella.
def get_server_rankings_from_file(jf, cntr, AU):
  server_set = set() # The set of the distincts server domains 
  f_server_dict = {} # The dictionary of the server domains as keys and their ranking as values
  lines = read_file(jf) # Parse the file
  if not lines == None: 
    for line in lines: 
      jobj = json.loads(line) # Parse the JSON

      if 'cisco_domain' in jobj: # Keep the server domain or cisco_domain depending on the dataset
        dmn = jobj['cisco_domain'] # The Umbrella dataset has domain and cisco_domain. Keep the cisco_domain.
      else: 
        dmn = jobj['domain'] # The Alexa dataset has only domains

      if update_set(server_set, dmn): # If it is the first time we see the server domain
        if 'cisco_rank' in jobj and AU == "Umbrella":  # If it is Umbrella,  
          f_server_dict[dmn] = jobj['cisco_rank'] # add the Umbrella ranking in the server dictionary 
          if not args.csv: 
            if (int(jobj['cisco_rank']) % PROGRESS_PRINT_MODULO == 0): # For every PROGRESS_PRINT_MODULO servers, 
              print(".", end ="", flush=True) # print progress dot
        else:  # If it is Alexa,
          f_server_dict[dmn] = jobj['alexa_rank'] # add the Alexa ranking in the server dictionary 
          if not args.csv: 
            if (int(jobj['alexa_rank']) % PROGRESS_PRINT_MODULO == 0): # For every PROGRESS_PRINT_MODULO servers, 
              print(".", end ="", flush=True) # print progress dot
      else:  # Otherwise, if we have seen this server before,  
        if 'cisco_rank' in jobj and AU == "Umbrella": # if it is Umbrella, 
          if not f_server_dict[dmn] == jobj['cisco_rank']: # alert that two cisco_rank rankings for that server differed
            print("Server", dmn, "had entries with different Umbrella rankings in the dataset. ") 
            break # and Exit
        else: # If it is Alexa, 
          if not f_server_dict[dmn] == jobj['alexa_rank']: # alert that two alexa_rank ranking for that server differed
            print("Server", dmn, "had entries with different Alexa rankings in the dataset. ")
            break # And Exit
      if len(server_set) == cntr: # Exit when exceeding the maximum server counter
        break 
  #print("")
  return server_set, f_server_dict


# Returns the diff of the rankings of the server domains provided as values and keys respectively in two dictionaries 
# passed as input. For a domain that is in one dictionary and not the other it adds 1000000, othewise it adds the diff 
# of the two rankings. The returned metric is divided by 1000 in the end.
def server_ranking_diff_metric(sdict1, sdict2): 
  # Always start from the dictionary that has more items so we don't undercalculate the difference.
  if len(sdict1) > len (sdict2):  
    sd1 = sdict1
    sd2 = sdict2
  else: 
    sd1 = sdict2
    sd2 = sdict1
  metric1 = 0
  metric2 = 0
  for s in sd1: 
    if not args.csv: 
      if (int(sd1[s]) % PROGRESS_PRINT_MODULO == 0): # For every PROGRESS_PRINT_MODULO servers
        print("@", end ="", flush=True) # print progress
    if s in sd2: # For servers that exist in both dictionaries
      metric1 += abs(int(sd1[s])-int(sd2[s])) # Add the ranking diff to the metric
  # For server domains that is in one dictionary and not the other, add 1000000
  metric2 = (server_count_diff(sdict1, sdict2)+server_count_diff(sdict2, sdict1))*1000000 
  #print(metric)
  return (metric1+metric2) / 1000 # Return the metric divided by 1000 in the end.


# Returns the # of servers that exist in the first dictionary provided as input, but not the second. 
# The two dictionaries provided as input parameters have the server domain as the key and the 
# Alexa/Umbreall ranking as value. The rankings are not used for the metric calculation. 
def server_count_diff(d1, d2):
  metric = 0 
  for s in d1: 
    if not args.csv: 
      if (int(d1[s]) % PROGRESS_PRINT_MODULO == 0): # For every PROGRESS_PRINT_MODULO servers
        print("*", end ="", flush=True) # print progress dot
    if s not in d2: 
      metric += 1
  return metric


# Returns the # of servers that exist in one of the two dictionaries provided as input, but not both.
# The two dictionaries provided as input parameters have the server domain as the key and the 
# Alexa/Umbreall ranking as value. The rankings are not used for the metric calculation.  
def server_count_diff_metric(sdict1, sdict2): 
  diff = server_count_diff(sdict1, sdict2) # Get the # of servers from the first dictionary which don't exist in the second.
  diff += server_count_diff(sdict2, sdict1) # Get the # of servers from the second dictionary which don't exist in the first.
  # print(diff, ",", (len(sdict1)+len(sdict2)))
  return diff * 100 / (len(sdict1)+len(sdict2)) # Return metric



if __name__ == "__main__":

  PROGRESS_PRINT_MODULO = 1000 # To be used to print progress dots as the ICAs are being processed.

  # Input parameters
  paramparser = argparse.ArgumentParser(description='Analyze and Comprate TopX server datasets.')
  paramparser.add_argument('f1', 
                           help="TopX Alexa File")
  paramparser.add_argument('f2',
                           help="TopX Cisco Umbrella File")
  paramparser.add_argument("--csv", action='store_true', 
			help="CSV statistics output.")
  paramparser.add_argument("--top", type=int, nargs='?', default=1000000, # Process only the top # of servers in the files.
                           help="Number of servers to fetch ICAs for. Default is 1M.")
  args = paramparser.parse_args()

  '''# Pring input arguments for testing 
  print(args.f1)
  print(args.f2)
  print(args.top)'''

  # Starting 
  #print ("Comparing", args.f1, "and", args.f2, "datasets.")

  max_srv = args.top # counter for the top number of servers to process from the files
  jf1 = args.f1 # the first JSON dataset.
  jf2 = args.f2 # the second JSON dataset.

  A_server_set, A_server_dict = get_server_rankings_from_file(jf1, max_srv, "Alexa")
  #print(f1_server_set)
  #print(f1_server_dict)
  U_server_set, U_server_dict = get_server_rankings_from_file(jf2, max_srv, "Umbrella")
  #print(f2_server_set)
  #print(f2_server_dict)

  if not args.csv: 
    #print("\nAlexa-Alexa, Umbrella-Umbrella simple server diff % metrics (should be 0): ", server_count_diff_metric(A_server_dict, A_server_dict),
    #      ",", server_count_diff_metric(U_server_dict, U_server_dict)) # should be 0 because we are comparing the same files 
    print("\nAlexa-Umbrella simple server diff % metric: ", server_count_diff_metric(A_server_dict, U_server_dict))
    #print("\nUmbrella-Alexa simple server diff % metric: ", server_count_diff_metric(U_server_dict, A_server_dict)) # should be the same as above
  
    #print("\nAlexa-Alexa, Umbrella-Umbrella ranking diff metrics (should be 0): ", server_ranking_diff_metric(A_server_dict, A_server_dict),
    #      ",", server_ranking_diff_metric(U_server_dict, U_server_dict)) # should be 0 because we are comparing the same files 
    print("\nAlexa-Umbrella ranking diff metric: ", server_ranking_diff_metric(A_server_dict, U_server_dict))
    #print("\nUmbrella-Alexa ranking diff metric: ", server_ranking_diff_metric(U_server_dict, A_server_dict)) # should be the same as above
  else: 
    print(jf1, ",", jf2, ",", server_count_diff_metric(A_server_dict, U_server_dict), ",", server_ranking_diff_metric(A_server_dict, U_server_dict))

