#!/usr/bin/env python3

# Run this script to dump your lspci to the file.
# Then you can share resulting file and it may be used for debugging.

import pickle

from pylspci.parsers import VerboseParser
lspci_devices = VerboseParser().run()

with open("lspci_devices_dump.bin", "wb") as fp:   #Pickling
    pickle.dump(lspci_devices, fp)
