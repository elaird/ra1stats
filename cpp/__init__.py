import ROOT as r
import os


def compile(dir="cpp",
            files=["StandardHypoTestInvDemo.cxx",
                   #"NckwWorkspace.cxx", "RooLognormal2.cxx",
                   "Poisson.cxx", "Gaussian.cxx", "Lognormal.cxx",
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

    r.gSystem.SetBuildDir(dir, True)
    r.gSystem.SetIncludePath(incPaths)
    r.gSystem.SetLinkedLibs(libPaths + libs)
    for f in files:
        r.gSystem.CompileMacro("%s/%s" % (dir, f), "kc")

    os.system("cd %s; make -s" % dir)


def load(dir="cpp"):
    r.gSystem.AddDynamicPath(dir)
    for name in ["Gaussian", "Lognormal", "Poisson", "StandardHypoTestInvDemo"]:
        r.gSystem.Load("%s_cxx.so" % name)
