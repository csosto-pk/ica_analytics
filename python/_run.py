#!/usr/bin/python3

import csv, os.path
from pprint import pprint

from ica_used import *

PROGRESS_PRINT_CTR = 10

# Starting 
print ("Fetching the Top...")

ica_list = list() # List with distinct ICA certificates
dest_list = ["cisco.com", "cisco.com", "google.com", "google.com", "microsoft.com", ]

# Open the file as f.
# The function readlines() reads the file.
# Define a filename.
filename = "../data/umbrella-top-1m.csv_4-5-2021.csv"
rows = 10000
if not os.path.isfile(filename):
    print('File does not exist.')
else:
  with open(filename) as csv_file:
      csv_reader = csv.reader(csv_file, delimiter=',')
      for row in csv_reader: 
          if (int(row[0]) % PROGRESS_PRINT_CTR == 0): 
            print(".", end ="", flush=True)
          if int(row[0]) > rows: 
             break
          else: 
             #print(row[1], end =" ")
             certs = get_certificate_chain(row[1]) # Fetch the ICA cert chain from the server
             #pprint(certs)
             #TODO: If certs are empty, then get one more entry because this was a fluke. rows++
             for cert in certs: 
               #if (cert.get_subject() != cert.get_issuer()): # if it is not a root CA cert
               if not list_contains_cert(ica_list, cert): # if it does not exist in the list 
                 ica_list.append(cert)    # only then add it to it

'''
for s in dest_list: 
             certs = get_certificate_chain(s) # Fetch the ICA cert chain from the server
             for cert in certs: 
               #if (cert.get_subject() != cert.get_issuer()): # if it is not a root CA cert
               if not list_contains_cert(ica_list, cert): # if it does not exist in the list 
                 ica_list.append(cert)    # only then add it to it
'''

#print_certs_list(ica_list)
print("")
print_list_cert_count(ica_list)


