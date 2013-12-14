import collections
import ROOT as r


def subDirHistos(fileName="", check1D=False, check2D=False):
    oneD = []
    twoD = []
    out = {}

    f = r.TFile(fileName)
    for subDirKey in f.GetListOfKeys():
        subDir = subDirKey.GetName()
        out[subDir] = {}
        for hKey in f.Get(subDir).GetListOfKeys():
            name = hKey.GetName()
            h = f.Get("%s/%s" % (subDir, name)).Clone("%s_%s" % (subDir, name))
            h.SetDirectory(0)
            out[subDir][name] = h
            if h.ClassName()[:3] == "TH2":
                twoD.append(h)
            if h.ClassName()[:3] == "TH1":
                oneD.append(h)
    f.Close()
    if check2D:
        checkHistoBinning(twoD)
    if check1D:
        checkHistoBinning(oneD)
    return out


def checkHistoBinning(histoList=[]):
    def axisStuff(axis):
        return (axis.GetXmin(), axis.GetXmax(), axis.GetNbins())

    def properties(histos):
        out = collections.defaultdict(list)
        for h in histos:
            try:
                out["type"].append(type(h))
                out["x"].append(axisStuff(h.GetXaxis()))
                out["y"].append(axisStuff(h.GetYaxis()))
                out["z"].append(axisStuff(h.GetZaxis()))
            except AttributeError as ae:
                h.Print()
                raise ae
        return out

    for axis, values in properties(histoList).iteritems():
        #print "Here are the %s binnings: %s"%(axis, str(values))
        sv = set(values)
        if len(sv) != 1:
            print "The %s binnings do not match: %s" % (axis, str(values))
            for h in histoList:
                print h, properties([h])
            assert False


def print_unpack(item, level=0, ending_comma=False):
    if not isinstance(item, dict):
        if not isinstance(item, collections.Iterable):
            print "\t"*level, "{item:.4}".format(item=item),
            if ending_comma:
                print ","
            else:
                print
        else:
            s = "(" if isinstance(item, tuple) else "["
            e = ")" if isinstance(item, tuple) else "]"
            print "\t"*level, s,
            for i in item:
                print "{i:.4},".format(i=i),
            print e,
            if ending_comma:
                print ","
    else:
        print "\t"*level, "{"
        for key, value in item.iteritems():
            print "\t"*(level+1),
            keystring = '"%s"' % key
            print '{k:20} : '.format(k=keystring),
            print_unpack(value, 0, True)
        print "\t"*level, "}"


def suffix(yMin=None, yMax=None):
    out = ""
    if yMin is not None:
        out += "%s-" % str(yMin)
    if yMax is not None:
        out += "-%s" % str(yMax)
    if out:
        out = "_"+out
    return out


def projection(h2=None, name="", yMin=None, yMax=None):
    axis = h2.GetYaxis()
    firstBin = 0 if yMin is None else axis.FindBin(yMin)
    lastBin = 1 + axis.GetNbins() if yMax is None else axis.FindBin(yMax)
    return h2.ProjectionX(name, firstBin, lastBin, "e")


def sliced(dir="", fileName="", yMin=None, yMax=None):
    perBox = subDirHistos("%s/%s" % (dir, fileName),
                          check2D=True,
                          check1D=False)
    out = {}
    for box, perSample in perBox.iteritems():
        out[box] = {}
        for sampleName, histo in perSample.iteritems():
            if histo.ClassName()[:3] == "TH1":
                out[box][sampleName] = histo
            else:
                name = box + sampleName + suffix(yMin, yMax)
                out[box][sampleName] = projection(h2=histo,
                                                  name=name,
                                                  yMin=yMin,
                                                  yMax=yMax)
    return out


class container(object):
    _mcExpectationsBeforeTrigger = {}
    _mcStatError = {}
    _observations = {}
    _lumi = {}


def histoSum(name="", histos=[]):
    if not histos:
        return None
    out = histos[0].Clone(name)
    for h in histos[1:]:
        out.Add(h)
    return out


def toSum(histos={}, sampleNames=[], msg=""):
    out = []
    for sn in sampleNames:
        if sn in histos:
            out.append(histos[sn])
        else:
            print "ERROR (%s): sample %s not found" % (msg, sn)
            print "Available:", histos.keys()
            exit()
    return out


def structured(histosPerBox={},
               mcLumiKey="",
               dataLumiKey="",
               mapPerBox={},
               ):
    assert mcLumiKey
    assert dataLumiKey

    out = container()
    for box, histos in histosPerBox.iteritems():
        for outKey, sampleNames in mapPerBox[box].iteritems():
            h = histoSum(name="%s_%s" % (box, outKey),
                         histos=toSum(histos,
                                      sampleNames,
                                      msg="box=%s, outKey=%s" % (box, outKey)
                                      ),
                         )

            bins = range(1, 1+h.GetNbinsX())
            values = tuple([h.GetBinContent(iBin) for iBin in bins])
            errors = tuple([h.GetBinError(iBin) for iBin in bins])
            if outKey[0] == "n":
                out._observations[outKey] = values
                out._lumi[outKey[1:].lower()] = histos[dataLumiKey].GetBinContent(1)
            else:
                out._mcExpectationsBeforeTrigger[outKey] = values
                out._mcStatError[outKey+"Err"] = errors
                out._lumi[outKey] = histos[mcLumiKey].GetBinContent(1)

    assert h, "No example found!"
    xbins = range(1, 1+h.GetNbinsX())
    out._htBinLowerEdges = [h.GetXaxis().GetBinLowEdge(bin) for bin in xbins]
    out._htMaxForPlot = h.GetXaxis().GetBinUpEdge(len(xbins))
    return out


def printCategory(name="", slice=None):
    print "class data_%s(data) :" % name
    print "    def _fill(self) :"
    for attr_name in dir(slice):
        if not "__" in attr_name:
            attr_data = getattr(slice, attr_name)
            print "{space}{classname}.{obj} = ".format(space=" "*8,
                                                       classname="self",
                                                       obj=attr_name),
            print_unpack(attr_data, 1)
            print
    print "%scommon(self)" % (" "*8)
    print "\n"


def printAll(dir="",
             files={},
             mcLumiKey="",
             dataLumiKey="",
             mapPerBox={},
             yMin=None,
             yMax=None,
             ):
    for category, fileName in sorted(files.iteritems()):
        histosPerBox = sliced(dir=dir,
                              fileName=fileName,
                              yMin=yMin,
                              yMax=yMax,
                              )

        slice = structured(histosPerBox=histosPerBox,
                           mcLumiKey=mcLumiKey,
                           dataLumiKey=dataLumiKey,
                           mapPerBox=mapPerBox,
                           )

        printCategory(name=category, slice=slice)
