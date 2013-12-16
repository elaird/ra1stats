import ROOT as r
import os


def compile(files=["cpp/StandardHypoTestInvDemo.cxx",
                   #"cpp/NckwWorkspace.cxx", "cpp/RooLognormal2.cxx",
                   "cpp/Poisson.cxx", "cpp/Gaussian.cxx", "cpp/Lognormal.cxx"],
            root=["`root-config --cflags --libs`"],
            flags=" -W".join(["", "all", "extra"]),
            libs=" -l".join(["", "RooFitCore", "RooFit", "RooStats"]),
            libPaths=" -L".join(["", "${ROOFITSYS}/lib"]),
            incPaths=" -I".join(["", "${ROOFITSYS}/include"]),
            ):

    #r.gSystem.SetBuildDir("cpp")
    r.gSystem.SetIncludePath(incPaths)
    r.gSystem.SetLinkedLibs(libPaths + libs)
    for f in files:
        r.gROOT.LoadMacro("%s+" % f)

    cmd = " ".join(["g++", "-o cpp/drive", "cpp/drive.cxx"] + root)
    cmd += " ".join([flags, libs, libPaths, incPaths])
    os.system(cmd)
