#!/usr/bin/python3

# Returns 1 if a certificate exists in a certificate list.
def list_contains_cert(ica_list, crt):
  for ic in ica_list: 
    if crt.digest("sha256") == ic.digest("sha256"):
      return 1
  return 0

def update_ica_list(icas, ica_certs):
  for cert in ica_certs: 
    if not list_contains_cert(icas, cert): # if it does not exist in the list 
      icas.append(cert)    # only then add it to it

# Prints Subject and Issuer information of a cert.
def print_cert(c): 
   print("Subject: CN=", c.get_subject().CN, ", O=", c.get_subject().O, ", C=", c.get_subject().C, 
         "Issuer: CN=", c.get_issuer().CN, ", O=", c.get_issuer().O, ", C=", c.get_issuer().C)

# Prints Subject and Issuer information of the certs in a list. 
def print_certs_list(c_list): 
  for c in c_list:
     print_cert(c)

# Prints number or elements in a list 
def print_list_cert_count(c_list): 
  print("Distinct ICA certs Processing: ", len(c_list))

ica_list = list() # List with distinct ICA certificates

print_certs_list(ica_list)
#print_list_cert_count(ica_list)
