#!/usr/bin/env python
import sys

def points() :
    return [(int(sys.argv[i]), int(sys.argv[i+1]), int(sys.argv[i+2])) for i in range(4, len(sys.argv), 3)]

def go() :
    for point in points() :
        import fresh
        fresh.go()

profile = False
if profile :
    import cProfile
    cProfile.run("go()", "resultProfile.out")
else :
    go()
