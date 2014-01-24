#!/usr/bin/env python

import os
import sys

sys.path.append(os.path.dirname(__file__)+"/..")

for file in sorted(os.listdir(os.path.dirname(__file__))):
    if not file.endswith(".py") or file in ["__init__.py", "check.py"]:
        continue
    module = file[:-3]
    print module
    exec("from likelihood import %s" % module)
    exec("%s.%s()" % (module, module))
    print
