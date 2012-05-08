import ROOT as r

def compile(files = ["cpp/StandardHypoTestInvDemo.cxx","cpp/Poisson.cxx","cpp/Gaussian.cxx"]) :
    for f in files :
        r.gROOT.LoadMacro("%s+"%f)