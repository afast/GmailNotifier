#!/usr/bin/env python

"""
create_keys.py

Create and save public and private keys
"""

import os
import ezPyCrypto

directory=os.path.dirname(os.path.realpath(__file__))
# Create a key object
k = ezPyCrypto.key(1280)

# Export private and public/private keys
publicKey = k.exportKey()
publicAndPrivateKey = k.exportKeyPrivate()

# Save these to disk (. to hide them in linux at least)
fd = open(directory+"/.ex_mykey.pub", "w")
fd.write(publicKey)
fd.close()

fd = open(directory+"/.ex_mykey.priv", "w")
fd.write(publicAndPrivateKey)
fd.close()
