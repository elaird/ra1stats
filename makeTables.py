#!/usr/bin/env python

import math
from inputData import data2011

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

def oneRow(label = "", labelWidth = 23, entryList = [], entryWidth = 30, hline = (False,False), extra = "") :
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
            s += oneRow(label = row["label"], entryList = row["entryFunc"](data, indices, *row["args"] if "args" in row else ()),
                        entryWidth = row["entryWidth"] if "entryWidth" in row else 30)
    s += endTable()
    return s

#alphaT ratio
def tailCounts(data, indices, *args) :
    return ["%d"%data.observations()["nHad"][i] for i in indices]

def bulkCounts(data, indices, *args) :
    return ["%4.2e"%data.observations()["nHadBulk"][i] for i in indices]

def alphaTratios(data, indices, *args) :
    tail = data.observations()["nHad"]
    bulk = data.observations()["nHadBulk"]
    return ["%4.2e $\pm$ %4.2e_{stat}"%(tail[i]/(0.0+bulk[i]), max(zeroObsUpperLimit, math.sqrt(tail[i]))/(0.0+bulk[i])) for i in indices]

def RalphaT(data) :
    return oneTable(data,
                    caption = r'''$\RaT$ distribution '''+"%g"%data.lumi()["had"]+r'''pb$^{-1}$''',
                    label = "results-HT",
                    rows = [{"label": r'''$\alt > 0.55$''', "entryFunc":tailCounts},
                            {"label": r'''$\alt < 0.55$''', "entryFunc":bulkCounts},
                            {"label": r'''$\RaT$''',        "entryFunc":alphaTratios},
                            ])

#EWK helpers
def truncate(t, index = 2) :
    l = list(t)
    return tuple(l[:index] + [sum(l[index:])]*(len(l)-index))

def mcYieldHadLumi(data, indices, *args) :
    return ["%4.1f"%data.mcExpectations()[args[0]][i] for i in indices]

def mcYieldOtherLumi(data, indices, *args) :
    mcOther = data.mcExpectations()[args[0]]
    lumiOther = data.lumi()[args[1]]
    lumiHad   = data.lumi()[args[2]]
    return ["%4.1f"%(mcOther[i]*lumiHad/lumiOther) for i in indices]

def mcRatio(data, indices, *args) :
    mcPhot = truncate(data.mcExpectations()[args[0]])
    mcZinv = truncate(data.mcExpectations()[args[1]])
    lumiPhot = data.lumi()[args[2]]
    lumiHad  = data.lumi()[args[3]]
    return ["%4.2f"%(mcZinv[i]/(mcPhot[i]*lumiHad/lumiPhot)) for i in indices]

def dataYieldOtherLumi(data, indices, *args) :
    lumiPhot = data.lumi()[args[1]]
    lumiHad = data.lumi()[args[2]]
    return ["%5.1f"%(data.observations()[args[0]][i]*lumiHad/lumiPhot) for i in indices]

def error(obs) :
    d = {}
    d[0] = 1.15
    d[1] = 1.36
    if obs in d : return d[obs]
    else : return math.sqrt(obs)
    
def prediction(data, indices, *args) :
    def oneString(obs, ratio, sysFactor = 1.0) :
        return "%5.1f $\pm$ %5.1f_{stat} %s"%(obs*ratio, error(obs)*ratio, "" if not obs else " $\pm$ %5.1f_{syst}"%(obs*ratio*sysFactor))
    mcPhot = truncate(data.mcExpectations()[args[1]])
    mcZinv = truncate(data.mcExpectations()[args[2]])
    return [oneString(data.observations()[args[0]][i], mcZinv[i]/mcPhot[i], data.fixedParameters()[args[3]]) for i in indices]

#photon to Z
def photon(data) :
    return oneTable(data,
                    caption = r'''Photon Sample Predictions '''+"%g"%data.lumi()["had"]+r'''pb$^{-1}$''',
                    label = "results-PHOTON",
                    rows = [{"label": r'''MC $\znunu$''',          "entryFunc":mcYieldHadLumi,    "args":("mcZinv",)},
                            {"label": r'''MC $\gamma +$~jets''',   "entryFunc":mcYieldOtherLumi,  "args":("mcPhot", "phot", "had")},
                            {"label": r'''MC Ratio''',             "entryFunc":mcRatio,           "args":("mcPhot", "mcZinv", "phot", "had")},
                            {"label": r'''Data $\gamma +$~jets''', "entryFunc":dataYieldOtherLumi,"args":("nPhot", "phot", "had")},
                            {"label": r'''$\znunu$ Prediction''',  "entryFunc":prediction,        "args":("nPhot", "mcPhot", "mcZinv", "sigmaPhotZ")},
                            ])

#muon to W
def muon(data) :
    return oneTable(data,
                    caption = r'''Muon Sample Predictions '''+"%g"%data.lumi()["had"]+r'''pb$^{-1}$''',
                    label = "results-W",
                    rows = [{"label": r'''MC W + $\ttNew$''',         "entryFunc":mcYieldHadLumi,     "args":("mcTtw",)},
                            {"label": r'''MC $\mu +$~jets''',         "entryFunc":mcYieldOtherLumi,   "args":("mcMuon", "muon", "had")},
                            {"label": r'''MC Ratio''',                "entryFunc":mcRatio,            "args":("mcMuon", "mcTtw", "muon", "had")},
                            {"label": r'''Data $\mu +$~jets''',       "entryFunc":dataYieldOtherLumi, "args":("nMuon", "muon", "had")},
                            {"label": r'''W + $\ttNew$ Prediction''', "entryFunc":prediction,         "args":("nMuon", "mcMuon", "mcTtw", "sigmaMuonW")},
                            ])

#fit results
def dictFromFile(fileName) :
    out = {}
    f = open(fileName)
    for line in f :
        fields = line.split()
        key = fields[0]
        lumi = fields[1].replace("/pb]","").replace("[","")
        values = []
        for item in [item.replace(",","").replace("(","").replace(")","") for item in fields[2:]] :
            if item!="" : values.append(float(item))
        out[key] = (float(lumi), values)
    f.close()
    return out

def resultFromTxt(data, indices, *args) :
    return ["%5.1f"%data.txtData[args[0]][1][i] for i in indices]

def fitResults(data, fileName = "/home/hep/elaird1/81_fit/10_sm_only/v10/numbers.txt") :
    txtData = dictFromFile(fileName)
    assert len(set([len(value[1]) for value in txtData.values()]))==1
    data.txtData = txtData
    return oneTable(data,
                    caption = r'''Fit Results '''+"%g"%data.lumi()["had"]+r'''pb$^{-1}$''',
                    label = "results-fit",
                    rows = [{"label": r'''W + $\ttNew$ background''', "entryFunc":resultFromTxt,  "args":("ttw",)},
                            {"label": r'''$\znunu$ background''',     "entryFunc":resultFromTxt,  "args":("zInv",)},
                            {"label": r'''Total Background''',        "entryFunc":resultFromTxt,  "args":("hadB",)},
                            {"label": r'''Data''',                    "entryFunc":resultFromTxt,  "args":("nHad",)},
                            ])

    

zeroObsUpperLimit = 1.15
data = data2011()
print RalphaT(data)
print photon(data)
print muon(data)
print fitResults(data)
