import configuration as conf
import histogramProcessing as hp
import fresh

def writeSignalFiles() :
    hp.checkHistoBinning()
    
##merge functions
def mergedFile() :
    note = fresh.note(likelihoodSpec = conf.likelihood())
    return "%s_%s%s"%(conf.stringsNoArgs()["mergedFileStem"], note, ".root")

def mergePickledFiles(printExample = False) :
    example = hp.xsHisto()
    if printExample :
    	print "Here are the example binnings:"
    	print "x:",example.GetNbinsX(), example.GetXaxis().GetXmin(), example.GetXaxis().GetXmax()
    	print "y:",example.GetNbinsY(), example.GetYaxis().GetXmin(), example.GetYaxis().GetXmax()
    	print "z:",example.GetNbinsZ(), example.GetZaxis().GetXmin(), example.GetZaxis().GetXmax()

    histos = {}
    zTitles = {}
    
    for point in points() :
        fileName = conf.strings(*point)["pickledFileName"]
        if not os.path.exists(fileName) :
            print "skipping file",fileName            
        else :
            inFile = open(fileName)
            d = cPickle.load(inFile)
            inFile.close()
            for key,value in d.iteritems() :
                if type(value) is tuple :
                    content,zTitle = value
                else :
                    content = value
                    zTitle = ""
                if key not in histos :
                    histos[key] = example.Clone(key)
                    histos[key].Reset()
                    zTitles[key] = zTitle
                histos[key].SetBinContent(point[0], point[1], point[2], content)
            os.remove(fileName)

    for key,histo in histos.iteritems() :
        histo.GetZaxis().SetTitle(zTitles[key])

    f = r.TFile(mergedFile(), "RECREATE")
    for histo in histos.values() :
        histo.Write()
    f.Close()

