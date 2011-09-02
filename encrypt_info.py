#!/usr/bin/env python

"""
encrypt_info.py

Import a public key, and encrypt email and password
"""

import os
import sys
import ezPyCrypto

def usage():
    print "Usage:"
    print "encrypt_info.py email@example.com password"

if len(sys.argv) != 3:
    usage()
    exit()

email= sys.argv[1]
pwd= sys.argv[2]
print "Email: " + email
print "Password: " + pwd
print "Remember to escape weird characters like $ with a \ this way ~> \$"

directory=os.path.dirname(os.path.realpath(__file__))

# Create a key object
k = ezPyCrypto.key(1280)

# Read in the public key
fd = open(directory+"/.ex_mykey.pub", "rb")
print "Reading public key: .ex_mykey.pub"
pubkey = fd.read()
fd.close()

# import this public key
k.importKey(pubkey)

# Now encrypt the email against this public key
print "Encrypting email..."
enc = k.encString(email)

# Save the encrypted email to disk
print "Saving encrypted email to: email..."
fd = open(directory+"/email", "wb")
fd.write(enc)
fd.close()

# Now encrypt the password against this public key
print "encrypting password..."
enc = k.encString(pwd)

# Save the encrypted password to disk
print "Saving encrypted password to: pwd..."
fd = open(directory+"/pwd", "wb")
fd.write(enc)
fd.close()
print "Success"
