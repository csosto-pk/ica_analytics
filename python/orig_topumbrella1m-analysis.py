#!/usr/bin/python3

# Run python3 topumbrella1m-analysis.py ../data/umbrella/umbrella-top-1m-2021-02-15.csv ../data/umbrella/umbrella-top-1m-2021-03-15.csv --num_servers 100 
#  (sometimes it was getting stuck and it hung without connecting and printing dots and I had to press Control-C to get it to move to the next server)

import csv, os.path
import argparse
from pprint import pprint

PROGRESS_PRINT_CTR = 10

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

srv_cnt = args.num_servers # counter for the number of server to fetch ICAs for
sf1 = args.f1 # the first file that contains the servers
sf2 = args.f2 # the second file that contains the servers

f_set = set()
if not os.path.isfile(sf1):  
  print('File does not exist.') # Throw error if the file does not exist.
else:
  with open(sf1) as csv_f: # Open and read the file with the servers.
    csv_reader = csv.reader(csv_f, delimiter=',')
    for row in csv_reader: 
      if (int(row[0])>srv_cnt):
        break
      f_set.add(row[1])
      #print(row[1]) 

#print(f_set)

diff_element_cntr = 0
if not os.path.isfile(sf2):  
  print('File does not exist.') # Throw error if the file does not exist.
else:
  with open(sf2) as csv_f: # Open and read the file with the servers.
    csv_reader = csv.reader(csv_f, delimiter=',')
    for row in csv_reader:
      if (int(row[0])>srv_cnt):
        break
      #print(row[1])
      if not row[1] in f_set: 
        diff_element_cntr +=1 

print("Different elements in Top", srv_cnt, ":", diff_element_cntr, "(", diff_element_cntr*100/srv_cnt, "%)")

      
