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
    return l

def lumiString(l) :
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
            print "%10s %s %s"%(key, lumiString(lumi(data, key, value)), formatted(Value(value, truncate)))
        print


def toString(item) :
    if type(item) is float : return str(int(item))
    else : return str(item)

def RalphaT(data) :
    s = \
      r'''\begin{table}[ht!]
\caption{R$_{\alpha_{T}}$ distribution '''+"%g"%data.lumi()["had"]
    s += \
      r'''pb$^{-1}$} % title of table
\label{tab:results-HT}
\centering'''
    s += "\n\\begin{tabular}{ %s }"%("c".join(["|"]*(2+len(data.htBinLowerEdges())/2)))
    s += "\n\hline\n"

    just = 20
    w = 10
    tail = data.observations()["nHad"]
    bulk = data.observations()["nHadBulk"]
    fullBins = list(data.htBinLowerEdges()) + ["$\infty$"]
    for subTable in range(2) :
        start = 0 + subTable*len(fullBins)/2
        stop = 1 + (1+subTable)*len(fullBins)/2
        indices = range(start,stop-1)[:len(fullBins)/2]
        bins = fullBins[start:stop]
        s += "\n"
        s += "\scalht Bin (GeV)".ljust(just)+" & "+" & ".join([("%s--%s"%(toString(l), toString(u))).ljust(w) for l,u in zip(bins[:-1], bins[1:])])+r" \\  [0.5ex]"
        s += "\n\hline\n"
        s += r'''$\alpha_{T} > 0.55$'''.ljust(just)+" & "+" & ".join([("%d"%tail[i]).ljust(w) for i in indices])+r'''\\'''
        s += "\n"
        s += r'''$\alpha_{T} < 0.55$'''.ljust(just)+" & "+" & ".join([("%g"%bulk[i]).ljust(w) for i in indices])+r'''\\'''
        s += "\n\hline"

    s += r'''
\end{tabular}
\end{table}
'''
    return s

data = data2011()
print RalphaT(data)


