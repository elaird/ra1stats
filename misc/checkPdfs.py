#!/usr/bin/env python

import os

here = "plots"
there = "%s/119_2012_categories/v12/take14/13_cosmetic_updates/ht_distributions/" % os.environ["HOME"]

for fileName in os.listdir(here):
    if fileName[-4:] != ".pdf":
        continue
    if fileName not in os.listdir(there):
        continue
    print fileName
    os.system("/home/hep/elaird1/bin/pdfDiff %s/%s %s/%s" % (here, fileName, there, fileName))
