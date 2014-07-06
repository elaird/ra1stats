import os
import sys

# graphical hacks (white superscript)
nb = "n_{b}^{#color[0]{b}}"
nj = "n_{j}^{#color[0]{j}}"


def spec(name="", **kargs):
    exec("from likelihood import l%s" % name)
    llk = eval("l%s.l%s" % (name, name))
    return llk(**kargs)


class selection(object):
    def __init__(self, name="", note="", boxes=[], data=None,
                 bJets="", jets="", fZinvIni=0.5, fZinvRange=(0.0, 1.0),
                 AQcdIni=1.0e-2, AQcdMax=100.0, yAxisLogMinMax=(0.3, None),
                 zeroQcd=False, muonForFullEwk=False,
                 universalSystematics=False, universalKQcd=False):
        for item in ["name", "note", "boxes", "data", "bJets",
                     "jets", "fZinvIni", "fZinvRange", "yAxisLogMinMax",
                     "AQcdIni", "AQcdMax", "zeroQcd", "muonForFullEwk",
                     "universalSystematics", "universalKQcd"]:
            setattr(self, item, eval(item))
            assert type(boxes) is list

    def __str__(self):
        return "_".join([self.name, self.note, str(self.boxes)])


def sampleCode(boxes=[]):
    d = {"had": "h", "phot": "p", "muon": "1", "mumu": "2", "simple": "s"}
    out = [d[box] for box in boxes]
    return "".join(sorted(out))


class base(object):
    def separateSystObs(self):
        return self._separateSystObs

    def poi(self):
        #return {"var": (initialValue, min, max)}
        #return {"fZinv_55_0b_7": (0.5, 0.0, 1.0)}
        #return {"qcd_0b_le3j_0": (0.0, 0.0, 1.0e3)}
        #return {"k_qcd_0b_le3j": (3.0e-2, 0.01, 0.04)}
        #return {"ewk_0b_le3j_0": (2.22e4, 2.0e4, 2.5e4)}
        return {"f": self._poiIniMinMax}

    def REwk(self):
        return "" if self._ignoreHad else self._REwk

    def RQcd(self):
        return "Zero" if self._ignoreHad else self._RQcd

    def nFZinv(self):
        return "All" if self._ignoreHad else self._nFZinv

    def constrainQcdSlope(self):
        return False if self._ignoreHad else self._constrainQcdSlope

    def qcdParameterIsYield(self):
        return self._qcdParameterIsYield

    def initialValuesFromMuonSample(self):
        return self._initialValuesFromMuonSample

    def initialFZinvFromMc(self):
        return self._initialFZinvFromMc

    def lnUMax(self):
        return self._lnUMax

    def rhoSignalMin(self):
        return self._rhoSignalMin

    def legendTitle(self):
        more = " [QCD=0; NO HAD IN LLK]" if self._ignoreHad else ""
        return self._legendTitle + more

    def ignoreHad(self):
        return self._ignoreHad

    def selections(self):
        out = self._selections
        if self._whiteList:
            out = filter(lambda x: x.name in self._whiteList, out)
        if self._blackList:
            out = filter(lambda x: x.name not in self._blackList, out)
        return out

    def poiList(self):
        return self.poi().keys()

    def standardPoi(self):
        return self.poiList() == ["f"]

    def note(self):
        out = "%s_" % self._name

        if self.REwk():
            out += "REwk%s_" % self.REwk()

        out += "RQcd%s" % self.RQcd()

        if self.constrainQcdSlope():
            out += "Ext"

        out += "_fZinv%s" % self.nFZinv()
        if not self.standardPoi():
            out += "__".join(["poi"] + self.poiList())

        for selection in self.selections():
            code = sampleCode(selection.boxes)
            out += "_%s-%s" % (selection.name, code)
        return out

    def add(self, sel=[]):
        if self._ignoreHad:
            for s in sel:
                s.boxes.remove("had")
        self._selections += sel

    def _fill(self):
        raise Exception("NotImplemented", "Implement _fill(self)")

    def __init__(self, separateSystObs=True,
                 whiteList=[], blackList=[], ignoreHad=False):
        for item in ["separateSystObs",
                     "whiteList", "blackList", "ignoreHad"]:
            setattr(self, "_"+item, eval(item))

        self._name = ""
        self._REwk = None
        self._RQcd = None
        self._nFZinv = None
        self._qcdParameterIsYield = None
        self._constrainQcdSlope = None
        self._initialValuesFromMuonSample = None
        self._initialFZinvFromMc = None
        self._lnUMax = None
        self._selections = []
        self._poiIniMinMax = None
        self._rhoSignalMin = None

        self._fill()

        assert self._name
        #  assert self._lnUMax  # set in dumpHcgCards()
        assert type(self._poiIniMinMax) is tuple, self._poiIniMinMax
        assert len(self._poiIniMinMax) == 3, self._poiIniMinMax
        assert self._poiIniMinMax[1] <= self._poiIniMinMax[0] <= self._poiIniMinMax[2], self._poiIniMinMax
        assert type(self._rhoSignalMin) is float

        assert self._RQcd in ["Zero", "FallingExp"]
        assert self._nFZinv in ["All", "One", "Two"]
        assert self._REwk in ["", "Linear", "FallingExp", "Constant"]
        for item in ["qcdParameterIsYield", "constrainQcdSlope",
                     "initialValuesFromMuonSample",
                     "initialFZinvFromMc"]:
            assert getattr(self, "_"+item) in [False, True], item

    def __str__(self):
        sels = ",".join([x.name for x in self.selections()])
        return "%s   %s" % (self._name, sels)


    def checkHcgImpl(self):
        p = set(filter(lambda x: not x.startswith("_"), dir(self)))
        harmless = ["add", "checkHcgImpl", "constrainQcdSlope",
                    "dumpHcgCards", "formattedSelection", "preparedSelection",
                    "initialFZinvFromMc", "initialValuesFromMuonSample",
                    "legendTitle", "lnUMax", "note", "poi", "poiList",
                    "qcdParameterIsYield", "selections"]
        for item in harmless:
            p.remove(item)

        if not self.standardPoi():
            sys.exit("must have poi=f")
        else:
            p.remove("standardPoi")

        if self.rhoSignalMin():
            sys.exit("must have rhoSignalMin=0")
        else:
            p.remove("rhoSignalMin")

        if self.REwk():
            sys.exit("REwk vs. HT not supported")
        else:
            p.remove("REwk")

        if self.RQcd() != "Zero":
            sys.exit("RQcd vs. HT not supported")
        else:
            p.remove("RQcd")

        if self.ignoreHad():
            sys.exit("ignoreHad is not supported")
        else:
            p.remove("ignoreHad")

        if self.nFZinv() != "All":
            sys.exit("(nFZinv != \"All\") is not supported")
        else:
            p.remove("nFZinv")

        if not self.separateSystObs():
            print "WARNING: check non-separate systObs"
        p.remove("separateSystObs")

        if p:
            print self
            print sorted(p)
            sys.exit("likelihood.checkHgImpl(): deal with the above list.")


    def dumpHcgCards(self, signal={}):
        """
        https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideHiggsAnalysisCombinedLimit
        https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideCMSDataAnalysisSchool2014HiggsCombPropertiesExercise
        """

        self.checkHcgImpl()
        assert not signal
        print "Implement signal (including muon contamination)!"

        dirName = "l"+self._name
        if not os.path.exists(dirName):
            os.mkdir(dirName)

        fileNames = []
        for sel in self.selections():
            if sel.universalSystematics:
                print "Fail universalSystematics: skipping", sel
                continue
            if sel.universalKQcd:
                print "Fail universalKQcd: skipping", sel
                continue

            lines = self.formattedSelection(*self.preparedSelection(sel),
                                            label=sel.name)

            fileName = "%s/%s.txt" % (dirName, sel.name)
            f = open(fileName, "w")
            print >> f, "\n".join(lines)
            f.close()
            fileNames.append(fileName)

        return fileNames


    def preparedSelection(self, sel):
        if not self._lnUMax:
            self._lnUMax = 3.0
            print "WARNING: lnUMax not set.  Using %g." % self._lnUMax

        obs = []
        processes = []
        rates = []
        lumiUncs = []
        normZinv = {}
        normTtw = {}
        rhoPhotZ = {}
        rhoMumuZ = {}
        rhoMuonW = {}

        # processes to consider for each observed bin
        if sel.muonForFullEwk:
            procDct = {"had": ["s", "had"],
                       "muon": ["muon"],
                       }
        else:
            procDct = {"had": ["s", "ttw", "zinv"],
                       "muon": ["muon"],
                       "phot": ["phot"],
                       "mumu": ["mumu"],
                       }

        obsDct = sel.data.observations()
        mcExp = sel.data.mcExpectations()
        lumiDct = sel.data.lumi()
        systBins = sel.data.systBins()
        fixedPs = sel.data.fixedParameters()
        sigmaLumiLike = fixedPs.get("sigmaLumiLike")
        if not sigmaLumiLike:
            sigmaLumiLike = 0.10
            print "WARNING: using fake sigmaLumiLike for %s: %g" % (sel.name, sigmaLumiLike)

        for box in ["had", "muon", "phot", "mumu"]:
            if box not in sel.boxes:
                continue

            bins = []
            for i, n in enumerate(obsDct["n%s" % box.capitalize()]):
                bins.append(("%s%d" % (box, i), n))

                # initialize list for each background syst. parameter
                if box == "had":
                    # one per bin
                    normZinv[i] = []
                    normTtw[i] = []

                    # one per syst. region
                    pz = systBins.get("sigmaPhotZ")
                    if pz:
                        rhoPhotZ[pz[i]] = []

                    mz = systBins.get("sigmaMumuZ")
                    if mz:
                        rhoMumuZ[mz[i]] = []

                    mw = systBins.get("sigmaMuonW")
                    if mw:
                        rhoMuonW[mw[i]] = []

            obs += filter(lambda x: x[1] is not None, bins)  # FIXME

            minProc = len(processes)
            processes += procDct[box]  # FIXME

            for iProc, proc in enumerate(processes):
                if iProc < minProc:
                    continue

                for iBin, (name, n) in enumerate(bins):
                    if n is None:
                        continue

                    if iProc:
                        mcKey = "mc%s" % proc.capitalize()
                        rate = mcExp[mcKey][iBin] * lumiDct[box] / lumiDct[mcKey]
                        lumiUncs.append(None)
                    else:
                        rate = 1.23456789
                        lumiUncs.append(1.0 + sigmaLumiLike)
                    rates.append((name, iProc, proc, rate))

                    # background normalizations
                    for jBin in normZinv.keys():
                        if jBin == iBin:
                            if proc in ["zinv", "phot", "mumu"]:
                                normZinv[jBin].append(self._lnUMax)
                                normTtw[jBin].append(None)
                            elif proc in ["had", "ttw", "muon"]:  # "had" used when sel.muonForFullEwk
                                normZinv[jBin].append(None)
                                normTtw[jBin].append(self._lnUMax)
                            else:
                                normZinv[jBin].append(None)
                                normTtw[jBin].append(None)
                        else:
                            normZinv[jBin].append(None)
                            normTtw[jBin].append(None)

                    # translation syst.
                    for (dct, systKey, theProc) in [(rhoPhotZ, "sigmaPhotZ", "phot"),
                                                    (rhoMumuZ, "sigmaMumuZ", "mumu"),
                                                    (rhoMuonW, "sigmaMuonW", "muon"),
                                                    ]:
                        for jSystBin in dct.keys():
                            if proc == theProc and systBins[systKey][iBin] == jSystBin:
                                dct[jSystBin].append(1.0 + fixedPs[systKey][jSystBin])
                            else:
                                dct[jSystBin].append(None)

        return obs, processes, rates, lumiUncs, normZinv, normTtw, rhoPhotZ, rhoMumuZ, rhoMuonW


    def formattedSelection(self, obs, processes, rates,
                           lumiUncs, normZinv, normTtw,
                           rhoPhotZ, rhoMumuZ, rhoMuonW,
                           label=""):
        w1 = 25
        w2 = 9
        iFmt = "%" + str(w2) + "d"
        rFmt = "%" + str(w2) + ".3e"
        sFmt = "%" + str(w2) + ".2f"
        hyphens = "-" * 79
        lines = ["   ".join(["imax", "%3d" % len(obs), "number of categories"]),
                 "   ".join(["jmax", "%3d" % (len(processes) - 1), "number of samples minus one"]),
                 "   ".join(["kmax", "  *", "number of nuisance parameters"]),
                 hyphens,
                 "bin".ljust(w1)         + "  ".join([x[0].rjust(w2) for x in obs]),
                 "observation".ljust(w1) + "  ".join([iFmt % x[1]    for x in obs]),
                 hyphens,
                 "bin".ljust(w1)         + "  ".join([x[0].rjust(w2) for x in rates]),
                 "process".ljust(w1)     + "  ".join([iFmt % x[1]    for x in rates]),
                 "process".ljust(w1)     + "  ".join([x[2].rjust(w2) for x in rates]),
                 "rate".ljust(w1)        + "  ".join([rFmt % x[3]    for x in rates]),
                 hyphens,
                 "lumi lnN".ljust(w1)    + "  ".join([(sFmt % x) if x else "-".rjust(w2) for x in lumiUncs]),
                 ]

        for stem, form in [("normTtw",  "lnU"),
                           ("normZinv", "lnU"),
                           ("rhoPhotZ", "lnN"),
                           ("rhoMumuZ", "lnN"),
                           ("rhoMuonW", "lnN"),
                           ]:
            dct = eval(stem)
            for iParam, lst in sorted(dct.iteritems()):
                pName = "%s_%s_%d %s" % (stem, label, iParam, form)
                if not any(lst):
                    continue
                lines += [pName.ljust(w1)   + "  ".join([(sFmt % x) if x else "-".rjust(w2) for x in lst])]

        return lines
