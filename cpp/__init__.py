import ROOT as r
import os


def compile(files=["cpp/StandardHypoTestInvDemo.cxx",
                   #"cpp/NckwWorkspace.cxx", "cpp/RooLognormal2.cxx",
                   "cpp/Poisson.cxx", "cpp/Gaussian.cxx", "cpp/Lognormal.cxx",
                   ],
            ):
    root = "`root-config --cflags --libs`"
    flags = " -W".join(["", "all", "extra"])
    incPaths = " -I".join(["", "${ROOFITSYS}/include"]) if os.environ.get("ROOFITSYS") else ""
    libList = ["", "RooFitCore", "RooFit", "RooStats"]

    # https://sft.its.cern.ch/jira/browse/ROOT-4362
    if "5.32" in r.gROOT.GetVersion():
        libList.append("Cint")

    libs = " -l".join(libList)

    paths = []
    for var in ["ROOFITSYS", "ROOTSYS"]:
        if os.environ.get(var):
            paths.append("${%s}/lib" % var)
    libPaths = " -L".join([""] + paths) if paths else ""

    #r.gSystem.SetBuildDir("cpp")
    r.gSystem.SetIncludePath(incPaths)
    r.gSystem.SetLinkedLibs(libPaths + libs)
    for f in files:
        r.gROOT.LoadMacro("%s+" % f)

    cmd = "g++ -o cpp/drive cpp/drive.cxx "
    cmd += " ".join([root, flags, libs, libPaths, incPaths])
    os.system(cmd)
