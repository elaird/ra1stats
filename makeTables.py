#!/usr/bin/env python

import math,os
from collections import defaultdict

print "==================================================================="
print "*** makeTables.py: DATA PRINTING FUNCTIONALITY CURRENTLY BROKEN ***"
print "==================================================================="


#\usepackage{datetime}
def beginDocument(comment = r"\currenttime\ \today") :
    return r'''
\documentclass[8pt]{article}
\usepackage[landscape]{geometry}
\usepackage{xspace}
\newcommand{\alt}{\ensuremath{\alpha_{\rm{T}}}\xspace}
\newcommand{\RaT}{\ensuremath{R_{\alt}}\xspace}
\def\scalht{\mbox{$H_{\rm{T}}$}\xspace}
\newcommand{\ra}{\ensuremath{\rightarrow}}
\newcommand{\znunu}{\ensuremath{{\rm Z} \ra \nu\bar{\nu}}}
\newcommand{\ttNew}{\ensuremath{\rm{t}\bar{\rm{t}}}\xspace}
\newcommand\T{\rule{0pt}{2.6ex}}
\newcommand\B{\rule[-1.2ex]{0pt}{0pt}}
\begin{document}
'''#+comment

def endDocument() :
    return r'''\end{document}'''

def toString(item) :
    if type(item) is float : return str(int(item))
    else : return str(item)

def beginTable(data, caption = "", label = "", coldivisor = 2, divider = "|", alignment = "c") :
    s  = r'''\begin{table}[ht!]'''
    s += "\n\caption{%s}"%caption
    s += "\n\label{tab:%s}"%label
    s += "\n\centering"
    #s += "\n"+r'''\footnotesize'''
    s += "\n\\begin{tabular}{ %s }"%(alignment.join([divider]*(2+len(data.htBinLowerEdges())/coldivisor)))
    return s

def endTable( lastLine = True ) :
    et = ""
    if lastLine : et +="\hline"
    et += r'''

\end{tabular}
\end{table}
'''
    return et

def oneRow(label = "", labelWidth = 23, entryList = [], entryWidth = 30, hline = (False,False), extra = "") :
    s = ""
    if hline[0] : s += "\n\n\hline"
    s += "\n"+label.ljust(labelWidth)+" & "+" & ".join([entry.ljust(entryWidth) for entry in entryList])+r" \\ %s"%extra
    if hline[1] : s += "\n\hline"
    return s

def oneTable(data, caption = "", label = "", rows = [], coldivisor = 2, divider = "|", alignment = "c", lastLine = True) :
    s = beginTable(data, caption = caption, label = label, coldivisor = coldivisor, divider = divider, alignment = alignment)

    fullBins = list(data.htBinLowerEdges()) + ["$\infty$"]
    for subTable in range(coldivisor) :
        start = 0 + subTable*len(fullBins)/coldivisor
        stop = 1 + (1+subTable)*len(fullBins)/coldivisor
        indices = range(start,stop-1)[:len(fullBins)/coldivisor]
        bins = fullBins[start:stop]
        s += oneRow(label = "\scalht Bin (GeV)", entryList = [("%s--%s"%(toString(l), toString(u))) for l,u in zip(bins[:-1], bins[1:])],
                    hline = (True,True), extra = "[%fex]" % ( 1./coldivisor) )
        for row in rows :
            s += oneRow(label = row["label"], entryList = row["entryFunc"](data, indices, *row["args"] if "args" in row else ()),
                        entryWidth = row["entryWidth"] if "entryWidth" in row else 30, hline = row["hline"] if "hline" in row else (False,False))
    s += endTable( lastLine )
    return s

#alphaT ratio
def tailCounts(data, indices, *args) :
    return ["%d"%data.observations()["nHad"][i] for i in indices]

def bulkCounts(data, indices, *args) :
    return ["%4.2e"%data.observations()["nHadBulk"][i] for i in indices]

def alphaTratios(data, indices, *args) :
    tail = data.observations()["nHad"]
    bulk = data.observations()["nHadBulk"]
    return ["%4.2e $\pm$ %4.2e$_{stat}$"%(tail[i]/(0.0+bulk[i]), error(tail[i])/(0.0+bulk[i])) for i in indices]

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
    return t

#def truncate(t, index = 2) :
#    l = list(t)
#    return tuple(l[:index] + [sum(l[index:])]*(len(l)-index))

def nr(x, value = 0.0) :
    return x if x!=None else value

def purity(data, indices, *args) :
    p = data.purities()[args[0]]
    return ["%4.2f"%nr(p[i]) for i in indices]

def mcYieldHadLumi(data, indices, *args) :
    value = data.mcExpectations()[args[0]]
    error = data.mcStatError()[args[0]+"Err"]
    return ["%4.1f $\pm$ %4.1f$_{stat}$"%(nr(value[i]), nr(error[i])) for i in indices]

def mcYieldOtherLumi(data, indices, *args) :
    mcOther = data.mcExpectations()[args[0]]
    mcOtherErr = data.mcStatError()[args[0]+"Err"]
    lumiOther = data.lumi()[args[1]]
    lumiHad   = data.lumi()[args[2]]
    return ["%4.1f $\pm$ %4.1f$_{stat}$"%(nr(mcOther[i])*lumiHad/lumiOther, nr(mcOtherErr[i])*lumiHad/lumiOther) for i in indices]

def mcRatio(data, indices, *args) :
    mcPhot = truncate(data.mcExpectations()[args[0]])
    mcZinv = truncate(data.mcExpectations()[args[1]])
    lumiPhot = data.lumi()[args[2]]
    lumiHad  = data.lumi()[args[3]]
    return ["%4.2f"%(nr(mcZinv[i])/(nr(mcPhot[i], 1.0)*lumiHad/lumiPhot)) for i in indices]

def dataYieldOtherLumi(data, indices, *args) :
    lumiPhot = data.lumi()[args[1]]
    lumiHad = data.lumi()[args[2]]
    obs = data.observations()[args[0]]
    return ["%5.1f"%(nr(obs[i])*lumiHad/lumiPhot) for i in indices]

def error(obs) :
    d = {}
    d[0] = 1.15
    d[1] = 1.36
    if obs in d : return d[obs]
    else : return math.sqrt(obs)

def prediction(data, indices, *args) :
    def oneString(obs, ratio, sysFactor = 1.0) :
        return "%5.1f $\pm$ %5.1f$_{stat}$ %s"%(obs*ratio, error(obs)*ratio, "" if not obs else " $\pm$ %5.1f$_{syst}$"%(obs*ratio*sysFactor))
    mcPhot = truncate(data.mcExpectations()[args[1]] if args[1] in data.mcExpectations() else data.mcExtra()[args[1]])
    mcZinv = truncate(data.mcExpectations()[args[2]])
    obs = data.observations()[args[0]]
    print [mcPhot[i] for i in indices]
    return [oneString(nr(obs[i]), nr(mcZinv[i])/nr(mcPhot[i], 1.0), data.fixedParameters()[args[3]]) for i in indices]

#photon to Z
def photon(data) :
    return oneTable(data,
                    caption = r'''Photon Sample Predictions '''+"%g"%data.lumi()["had"]+r'''pb$^{-1}$''',
                    label = "results-PHOTON",
                    rows = [{"label": r'''MC $\znunu$''',          "entryFunc":mcYieldHadLumi,    "args":("mcZinv",)},
                            {"label": r'''MC $\gamma +$~jets''',   "entryFunc":mcYieldOtherLumi,  "args":("mcGjets", "phot", "had")},
                            {"label": r'''MC Ratio''',             "entryFunc":mcRatio,           "args":("mcGjets", "mcZinv", "phot", "had")},
                            {"label": r'''Data $\gamma +$~jets''', "entryFunc":dataYieldOtherLumi,"args":("nPhot", "phot", "had")},
                            {"label": r'''Sample Purity''',        "entryFunc":purity,            "args":("phot",)},
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
        lumi = fields[1].replace("/pb]","").replace("[","").replace("/fb]","")
        values = []
        for item in [item.replace(",","").replace("(","").replace(")","") for item in fields[2:]] :
            if item!="" : values.append(float(item))
        out[key] = (float(lumi), values)
    f.close()
    return out

def floatResultFromTxt(data, indices, *args) :
    return ["%5.1f"%data.txtData[args[0]][1][i] for i in indices]

def intResultFromTxt(data, indices, *args) :
    return ["%d"%data.txtData[args[0]][1][i] for i in indices]

def fitResults(data, fileName = "") :
    txtData = dictFromFile(fileName)
    assert len(set([len(value[1]) for value in txtData.values()]))==1
    data.txtData = txtData
    return oneTable(data,
                    caption = r'''Fit Results '''+"%g"%data.lumi()["had"]+r'''pb$^{-1}$''',
                    label = "results-fit",
                    rows = [{"label": r'''W + $\ttNew$ background''', "entryFunc":floatResultFromTxt,  "args":("ttw",)},
                            {"label": r'''$\znunu$ background''',     "entryFunc":floatResultFromTxt,  "args":("zInv",)},
                            {"label": r'''QCD background''',          "entryFunc":floatResultFromTxt,  "args":("qcd",)},
                            {"label": r'''Total Background''',        "entryFunc":floatResultFromTxt,  "args":("hadB",)},
                            {"label": r'''Data''',                    "entryFunc":intResultFromTxt,  "args":("nHad",)},
                            ])

def ensembleSplit(d, group = "had") :
    out = {}
    current_selection = None
    previous_selection = None
    selection_out = []
    for t in d : # expect t to be a tuple
        name,vals = t # expand the tuple
        if group in name :
            tokens = name.split("_")
            selection_id = tokens[-2]
            sbin = tokens[-1]
            # fix for first instance
            if current_selection is None :
                current_selection = selection_id
            previous_selection = current_selection
            current_selection = selection_id
            if current_selection != previous_selection and previous_selection is not None :
                out[previous_selection] = selection_out
                selection_out = []
            selection_out.append(vals)
    # get last one
    out[previous_selection] = selection_out
    return out

def ensembleSplit2(dct, group = "had") :
    out = defaultdict(list)
    for key,latex in dct.iteritems() :
        sample,aT,nB,iBin = key.split("_")
        if sample[:len(group)]!=group : continue
        out[nB] += [(iBin, latex)]

    for key in out.keys() :
        out[key] = map(lambda x:x[1],sorted(out[key]))
    return out

def ensembleRow( data, indices, d ) :
    if indices[-1] >= len(d) : 
        return d
    return [ d[index] for index in indices ]

def ensembleResultsBySample( d, data ) :
    samples =  ["had", "muon", "mumu", "phot"]
    samples_long =  [ "Hadronic", "$\mu$+jets",
                      "$\mu\mu$+jets", "$\gamma$+jets"]
    mc_titles   = [ "SM %s\T" % s for s in samples_long ]
    data_titles = [ "Data %s\T" % s for s in samples_long ]

    doc = beginDocument()
    for sample, sample_long, mc_title, data_title in zip( samples, samples_long, mc_titles, data_titles ) :
        # fill out MC values
        data_out = defaultdict(dict)
        mc_out = {}
        mc_out[mc_title] = ensembleSplit2(d, group = sample )
        if sample == "phot" :
            for selection, values in mc_out[mc_title].iteritems() :
                mc_out[mc_title][selection] = ["--", "--" ] + values

        titles = []
        selections = sorted(mc_out[mc_title].keys())
        for s in range( len(selections) ) :
            titles.append( mc_title+"" )
            titles.append( data_title+"" )

        # fill out data values
        for datum, selection in zip(data, selections) :
            obs = datum.observations()[ "n%s" % (sample.capitalize()) ]
            data_out[data_title][selection] = [ "$%d$" % int(x) if x is not None else "--" for x in obs ]

        # arrange into our final dictionary
        out = defaultdict(dict)
        for mc_key, data_key in zip( sorted(mc_out.keys()), sorted(data_out.keys()) ) :
            out[mc_key] = mc_out[mc_key]
            out[data_key] = data_out[data_key]

        # need to invert so we have "selection" : "DATA" : []
        #                                         "SM"   : []
        out_2 = defaultdict(dict)
        for title, sdict in out.iteritems() :
            for selection, values in sdict.iteritems() :
                out_2[selection][title] = values

        sel_substitutions = {
            '0b'   : '0 b-tags',
            '1b'   : '1 b-tags',
            '2b'   : '2 b-tags',
            'gt2b' : '$\geq$ 2 b-tags',
        }

        sel_key_it = []
        for key in sorted(out_2.keys()):
            sel_key_it.append(key)
            sel_key_it.append(key)

        doc += oneTable( data = data[s],
                         caption = "Fit summary (%s)" % sample_long,
                         label = "ensemble-%s" % "summary",
                         coldivisor = 1,
                         divider = "",
                         alignment = "l",
                         rows = [ {
                                   "label": "%s %s"  % ( sel_substitutions.get(sel_key,sel_key), title),
                                   "entryFunc":ensembleRow,
                                   "args": [out_2[sel_key][title]],
                                   "hline": (False,True) if "Data" in title else (False,False)
                                  }
                                  for sel_key,title in zip(sel_key_it, titles) if out_2[sel_key].get(title,False) ],
                         lastLine = False,
                       )
    doc += endDocument()
    write( doc, "ensemble_bySample.tex" )


def ensembleResultsBySelection( d, data ) :
    mc_out = {}
    data_out = defaultdict(dict)
    samples = [ "had", "muon", "mumu", "phot" ]

    mc_titles  = [ "SM hadronic\T", "SM $\mu$+jets\T",
                   "SM $\mu\mu$+jets\T", "SM $\gamma$+jets\T"]

    data_titles  = [ "Data hadronic\B", "Data $\mu$+jets\B",
                     "Data $\mu\mu$+jets\B", "Data $\gamma$+jets\B"]
    titles = []
    for dt, mct in zip(data_titles, mc_titles) :
        titles.append(mct+"")
        titles.append(dt+"")

    # fill out MC values
    for sample,title in zip(samples,mc_titles) :
        mc_out[title] = ensembleSplit2(d, group = sample )
        if sample == "phot" :
            for selection, values in mc_out[title].iteritems() :
                mc_out[title][selection] = ["--", "--" ] + values

    selections = sorted(mc_out[mc_titles[0]].keys())

    # fill out data values
    for datum, selection in zip(data, selections) :
        for data_title, sample in zip(data_titles, samples) :
            obs = datum.observations()[ "n%s" % (sample.capitalize()) ]
            data_out[data_title][selection] = [ "$%d$" % int(x) if x is not None else "--" for x in obs ]

    # arrange into our final dictionary
    out = {}
    for mc_key, data_key in zip( sorted(mc_out.keys()), sorted(data_out.keys()) ) :
        out[mc_key] = mc_out[mc_key]
        out[data_key] = data_out[data_key]

    doc = beginDocument()
    for s,selection in enumerate(selections) :
        doc += oneTable( data = data[s],
                         caption = selection,
                         label = "ensemble-%s" % selection,
                         coldivisor = 1,
                         divider = "",
                         alignment = "l",
                         rows = [ {"label": title, "entryFunc":ensembleRow, "args": [out[title][selection]], 
                                   "hline": (False,True) if "Data" in title else (False,False)} for title in titles if out[title].get(selection,False) ],
                         lastLine = False,
                       )
    doc += endDocument()

    write( doc, "ensemble_bySelection.tex" )


def document() :
    data = data2011()
    out = ""
    for blob in [beginDocument(), RalphaT(data), photon(data), muon(data),
                 ##fitResults(data, fileName = "/home/hep/elaird1/81_fit/10_sm_only/v10/numbers.txt")
                 ##fitResults(data, fileName = "/home/hep/elaird1/81_fit/10_sm_only/v11/numbers_602pb.txt"),
                 #fitResults(data, fileName = "/home/hep/elaird1/81_fit/10_sm_only/v13/numbers_v1.txt"),
                 #fitResults(data, fileName = "/home/hep/elaird1/81_fit/10_sm_only/v15/fitResults.txt"),
                 endDocument()] :
        out += blob
    return out

def write(doc, fileName = "") :
    assert fileName
    f = open(fileName, "w")
    f.write(doc)
    f.close()
    os.system("pdflatex %s"%fileName)

#write(document(), fileName = "tables.tex")
