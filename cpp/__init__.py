import ROOT as r

def compile(files = ["cpp/StandardHypoTestInvDemo.cxx","cpp/Poisson.cxx",
                     "cpp/Gaussian.cxx", "cpp/NckwWorkspace.cxx"]) :
    for f in files :
        r.gROOT.LoadMacro("%s+"%f)

    flags = ["-Wall", "-Wextra"]
    root = ["`root-config --cflags --libs`", "-lRooFit", "-lRooStats"]

    cmd = " ".join(["g++", "-o cpp/drive", "cpp/drive.cxx"]+flags+root)
    import os
    os.system(cmd)
