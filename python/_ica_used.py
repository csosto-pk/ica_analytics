#!/usr/bin/python3

# This Python program fetches the intermedite certificates excluding the server and RootCA cert) 
# from a list of servers. It stores them in a list and prints the list and the number of distinct 
# intermediate CA certs. 

import socket
from OpenSSL import SSL 

def get_certificate_chain(host):
    """
    Extracts the certificate chain from the provided host.
    params:
        host (str): hostname
    output:
        -list of certificates in the chain 
        -in case of exception (eg. timeout) returns -1
    """
    ica_certs_list = list()

    try:
        with cert_human.ssl_socket(host) as sock:
            leaf_cert = sock.get_peer_certificate() # fetch the server cert
            cert_chain = sock.get_peer_cert_chain()  # fetch the cert chain
            for ic in cert_chain: # for each cert in the chain
              # if it is not the server cert or a root CA cert
              if (leaf_cert.get_subject() != ic.get_subject() and ic.get_subject()!=ic.get_issuer()): 
                 ica_certs_list.append(ic) # add it to the Itermediate CA list
            return ica_certs_list
    except:
        try:
            dst = (host, 443)
            ctx = SSL.Context(SSL.SSLv23_METHOD)
            #timeout = socket.getdefaulttimeout()
            #print("System has default timeout of {} for create_connection".format(timeout))
            sock = socket.create_connection(dst,timeout=2.0)
            sock.settimeout(2.0)
            s = SSL.Connection(ctx, sock)
            sock.settimeout(None)
            s.set_connect_state()
            s.set_tlsext_host_name(dst[0].encode())
            s.sendall('QUIT\n\n')
            #  s.recv(16)
            leaf_cert = s.get_peer_certificate() # fetch the server cert
            cert_chain = s.get_peer_cert_chain() # fetch the cert chain (include server cert and root)
            for ic in cert_chain: # for each cert in the chain
              # if it is not the server cert or a root CA cert
              if (leaf_cert.get_subject() != ic.get_subject() and ic.get_subject()!=ic.get_issuer()): 
                 ica_certs_list.append(ic) # add it to the Itermediate CA list
            return ica_certs_list
        except: 
            return [] # Return empty list if something went wrong and we didn't get anything back

# Returns 1 if a certificate exists in a certificate list.
def list_contains_cert(ica_list, crt):
  for ic in ica_list: 
    if crt.get_subject()==ic.get_subject() and crt.get_issuer()==ic.get_issuer():
      return 1
  return 0

# Prints Subject and Issuer Information of the certs in a list. 
def print_cert(c): 
   print("s: CN=", c.get_subject().CN, ", O=", c.get_subject().O, ", C=", c.get_subject().C, 
         "i: CN=", c.get_issuer().CN, ", O=", c.get_issuer().O, ", C=", c.get_issuer().C)

# Prints Subject and Issuer Information of the certs in a list. 
def print_certs_list(c_list): 
  for c in c_list:
     print_cert(c)

# Prints number or elements in a list 
def print_list_cert_count(c_list): 
  print("Distinct ICA certs: ", len(c_list))



