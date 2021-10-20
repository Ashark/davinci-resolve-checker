#!/usr/bin/env python3

# For debugging https://github.com/Ashark/davinci-resolve-checker/pull/17

import pickle

from pylspci.parsers import VerboseParser
lspci_devices = VerboseParser().run()

with open("lspci_devices_dump.txt", "wb") as fp:   #Pickling
    pickle.dump(lspci_devices, fp)
