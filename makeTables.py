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

def beginTable(data, caption = "", label = "") :
    s  = r'''\begin{table}[ht!]'''
    s += "\n\caption{%s}"%caption
    s += "\n\label{tab:%s}"%label
    s += "\n\centering"
    s += "\n\\begin{tabular}{ %s }"%("c".join(["|"]*(2+len(data.htBinLowerEdges())/2)))
    return s

def endTable() :
    return r'''

\hline
\end{tabular}
\end{table}
'''

def oneRow(label = "", labelWidth = 20, entryList = [], entryWidth = 10, hline = (False,False), extra = "") :
    s = ""
    if hline[0] : s += "\n\n\hline"
    s += "\n"+label.ljust(labelWidth)+" & "+" & ".join([entry.ljust(entryWidth) for entry in entryList])+r" \\ %s"%extra
    if hline[1] : s += "\n\hline"
    return s

def oneTable(data, caption = "", label = "", rows = []) :
    s = beginTable(data, caption = caption, label = label)

    fullBins = list(data.htBinLowerEdges()) + ["$\infty$"]
    for subTable in range(2) :
        start = 0 + subTable*len(fullBins)/2
        stop = 1 + (1+subTable)*len(fullBins)/2
        indices = range(start,stop-1)[:len(fullBins)/2]
        bins = fullBins[start:stop]
        s += oneRow(label = "\scalht Bin (GeV)", entryList = [("%s--%s"%(toString(l), toString(u))) for l,u in zip(bins[:-1], bins[1:])],
                    hline = (True,True), extra = "[0.5ex]")
        for row in rows :
            s += oneRow(label = row["label"], entryList = row["entryFunc"](data, indices))
    s += endTable()
    return s

def tailCounts(data, indices) :
    return ["%d"%data.observations()["nHad"][i] for i in indices]

def bulkCounts(data, indices) :
    return ["%4.2e"%data.observations()["nHadBulk"][i] for i in indices]

def alphaTratios(data, indices) :
    tail = data.observations()["nHad"]
    bulk = data.observations()["nHadBulk"]
    return ["%4.2e"%(tail[i]/(0.0+bulk[i])) for i in indices]

def RalphaT(data) :
    return oneTable(data,
                    caption = r'''R$_{\alpha_{T}}$ distribution '''+"%g"%data.lumi()["had"]+r'''pb$^{-1}$}''',
                    label = "results-HT",
                    rows = [{"label": r'''$\alpha_{T} > 0.55$''', "entryFunc":tailCounts},
                            {"label": r'''$\alpha_{T} < 0.55$''', "entryFunc":bulkCounts},
                            {"label": r'''$R_{\alpha_{T}}$''',    "entryFunc":alphaTratios},
                            ])

data = data2011()
print RalphaT(data)


