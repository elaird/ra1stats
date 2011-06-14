#!/usr/bin/env python

from inputData import data2011

def printHtBins(data, truncate) :
    print "HT bins"
    print "-------"
    if truncate : print data.htBinLowerEdges()[:3]
    else :        print data.htBinLowerEdges()
        
    print

def lumi(data, key, value) :
    if type(value) is float : return ""
    lumiKey = key
    if lumiKey[0]=="n" :
        lumiKey = lumiKey[1:]
        lumiKey = lumiKey[0].swapcase()+lumiKey[1:]
        l = data.lumi()[lumiKey]
    else :
        aKey = lumiKey.replace("mc","").lower()
        if aKey in data.lumi() :
            l = data.lumi()[aKey]
        else :
            l = data.lumi()["had"]
    return "[%4.0f/pb]"%l

def Value(value, truncate) :
    if not truncate : return value
    if type(value)!= tuple : return value
    return tuple([value[0], value[1], sum(value[2:])])

def formatted(t) :
    if type(t) is float : return str(t)
    out = "("
    for i,item in enumerate(t) :
        out += "%3.2e"%item
        if i!=len(t)-1 : out += ", "
    return out+")"

def printYields(data, items = ["observations", "mcExpectations", "fixedParameters"], truncate = False) :
    for item in items :
        print item
        print "-"*len(item)
        d = getattr(data,item)()
        for key,value in d.iteritems() :
            print "%10s %s %s"%(key, lumi(data, key, value), formatted(Value(value, truncate)))
        print

truncate = False
data = data2011()
printHtBins(data, truncate = truncate)
printYields(data, truncate = truncate)
