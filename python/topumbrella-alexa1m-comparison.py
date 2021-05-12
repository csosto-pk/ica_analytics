#!/usr/bin/python3

# Run python3 topumbrella-alexa1m-comparison.py ../data/censys.io/example_umbrella1M.json ../data/censys.io/example_alexa1M.json --top 10


import os.path
import argparse
import json
from ica_analysis import update_set 

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
        else:  # If it is Umbrella
          f_server_dict[jobj['domain']] = jobj['umbrella_rank'] # Add the Umbrella  ranking in the server dictionary 
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
  return server_set, f_server_dict


if __name__ == "__main__":

  PROGRESS_PRINT_CTR = 10

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
  print(f1_server_set)
  print(f1_server_dict)
  f2_server_set, f2_server_dict = get_server_rankings_from_file(jf2, max_srv)
  print(f2_server_set)
  print(f2_server_dict)

  '''
    with open(jf1) as csv_f: # Open and read the file with the servers.
      csv_reader = csv.reader(csv_f, delimiter=',')
      for row in csv_reader: 
        if (int(row[0])>srv_cnt):
          break
        f_set.add(row[1])
        #print(row[1]) 
  '''
  #print(f_set)

  # flines = read_file(jf2)
  # f1_server_dict = {}

  '''
  diff_element_cntr = 0
  if not os.path.isfile(jf2):  
    print('File does not exist.') # Throw error if the file does not exist.
  else:
    with open(jf2) as csv_f: # Open and read the file with the servers.
      csv_reader = csv.reader(csv_f, delimiter=',')
      for row in csv_reader:
        if (int(row[0])>srv_cnt):
          break
        #print(row[1])
        if not row[1] in f_set: 
          diff_element_cntr +=1 

  print("Different elements in Top", srv_cnt, ":", diff_element_cntr, "(", diff_element_cntr*100/srv_cnt, "%)")
'''
