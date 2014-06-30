import likelihood


class l2012dev(likelihood.base):
    def _fill(self):
        self._name = self.__class__.__name__[1:]
        self._blackList += ["ge4b_le3j"]

        self._constrainQcdSlope = False
        self._qcdParameterIsYield = True
        self._initialValuesFromMuonSample = True
        self._initialFZinvFromMc = True
        self._poiIniMinMax = (0.0, 0.0, 1.0)
        self._rhoSignalMin = 0.0
        self._REwk = ""
        self._RQcd = "Zero"
        self._nFZinv = "All"
        self._legendTitle = "CMS Preliminary, 18.7 fb^{-1}, #sqrt{s} = 8 TeV"
        #from inputData.data2012dev import take13_blind_nHadFromFitWithTrigEff as module
        #from inputData.data2012dev import take13_semiBlind_nHadFromBlueFit as module
        from inputData.data2012dev import take13 as module

        #QCD test
        if False :
            print "WARNING: QCD test"
            self._constrainQcdSlope = False
            self._legendTitle += "[NO MHT/MET CUT]"
            from inputData.data2012hcp import take15a as module

        lst = []
        for b in ["0", "1", "2", "3", "ge4"] :
            for j in ["ge2", "le3", "ge4"][1:] :
                yAxisLogMinMax = {"0"  :(0.3, 5.0e4) if j=="le3" else (0.3, 5.0e4),
                                  "1"  :(0.3, 5.0e3) if j=="le3" else (0.3, 3.0e3),
                                  "2"  :(0.05,2.0e3) if j=="le3" else (0.3, 2.0e3),
                                  "3"  :(0.05,5.0e2),
                                  "ge4":(0.1, 1.0e2),
                                  }[b]  # out of date (commented below)

                fZinvIni = {"0b"  : {"ge2j":0.57, "le3j":0.5,  "ge4j":0.40},
                            "1b"  : {"ge2j":0.40, "le3j":0.40, "ge4j":0.20},
                            "2b"  : {"ge2j":0.10, "le3j":0.10, "ge4j":0.10},
                            "3b"  : {"ge2j":0.05, "le3j":0.05, "ge4j":0.05},
                            "ge4b": {"ge2j":0.01, "le3j":0.01, "ge4j":0.01},
                            }[b+"b"][j+"j"]

                name  = "%sb_%sj"%(b,j)
                if name == "ge4b_le3j":
                    continue

                #name  = "%sb_%sj_alphaTmuon"%(b,j)
                note  = "%s%s%s"%(likelihood.nb, "= " if "ge" not in b else "#", b)
                note += "; %s#%s"%(likelihood.nj, j)
                note = note.replace("ge","geq ").replace("le","leq ")

                if b in ["0", "1"]:
                    boxes = ["had", "muon", "phot", "mumu"]
                else:
                    boxes = ["had", "muon"]

                sel = likelihood.selection(name=name,
                                           note=note,
                                           boxes=boxes,
                                           muonForFullEwk=len(boxes) == 2,
                                           data=getattr(module, "data_%s" % name)(),
                                           bJets=("eq%sb" % b).replace("eqge", "ge"),
                                           jets="%sj" % j,
                                           fZinvIni=fZinvIni,
                                           AQcdIni=0.0,
                                           #yAxisLogMinMax=yAxisLogMinMax,
                                           )
                lst.append(sel)
        self.add(lst)
