#!/usr/bin/python3

# Original Top1M file comparison code. 
# It took the Alexa and Umbrella CSV files as input and was returning their statistical difference %. 

# Run is as 
# python3 topumbrella1m-analysis.py ../data/umbrella/umbrella-top-1m-2021-02-15.csv ../data/umbrella/umbrella-top-1m-2021-03-15.csv --num_servers 100 

import csv, os.path
import argparse
from pprint import pprint

PROGRESS_PRINT_CTR = 1000

paramparser = argparse.ArgumentParser(description='Analyze and Comprate TopX server datasets.')
paramparser.add_argument('f1', 
			help="TopX First File")
paramparser.add_argument('f2',
			help="TopX Second File")
paramparser.add_argument("--num_servers", type=int, nargs='?', default=1000000,
			help="Number of servers to fetch ICAs for. Default is 1M.")
args = paramparser.parse_args()

'''# Pring input arguments for testing 
print(args.f1)
print(args.f2)
print(args.num_servers)'''

# Starting 
print ("Comparing", args.f1, "and", args.f2, "datasets.")

srv_cnt = args.num_servers # counter for the number of servers
sf1 = args.f1 # the first file that contains the servers
sf2 = args.f2 # the second file that contains the servers

# Read the first file 
f_set = set()
if not os.path.isfile(sf1):  
  print('File does not exist.') # Throw error if the file does not exist.
else:
  with open(sf1) as csv_f: # Open and read the file with the servers.
    csv_reader = csv.reader(csv_f, delimiter=',')
    for row in csv_reader: 
      if (int(row[0])>srv_cnt): # Exit if you read more that the total servers passed as input
        break
      f_set.add(row[1])
      #print(row[1]) 

#print(f_set)

# Read the second file 
diff_element_cntr = 0
if not os.path.isfile(sf2):  
  print('File does not exist.') # Throw error if the file does not exist.
else:
  with open(sf2) as csv_f: # Open and read the file with the servers.
    csv_reader = csv.reader(csv_f, delimiter=',')
    for row in csv_reader:
      if (int(row[0])>srv_cnt): # Exit if you read more that the total servers passed as input
        break
      #print(row[1])
      if not row[1] in f_set: # Counter the different server domains
        diff_element_cntr +=1 

# Return the server domain difference %
print("Different elements in Top", srv_cnt, ":", diff_element_cntr, "(", diff_element_cntr*100/srv_cnt, "%)")

      
