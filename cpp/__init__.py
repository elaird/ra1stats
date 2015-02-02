import ROOT as r
import os


__root6 = r.gROOT.GetVersion().startswith("6.")


def compile_aclic(dir="cpp",
                  files=["StandardHypoTestInvDemo.cxx",
                         #"NckwWorkspace.cxx", "RooLognormal2.cxx",
                         "Poisson.cxx", "Gaussian.cxx", "Lognormal.cxx",
                         ],
                  ):
    root = "`root-config --cflags --libs`"
    flags = " -W".join(["", "all", "extra"])
    incPaths = " -I".join(["", "${ROOFITSYS}/include"]) if os.environ.get("ROOFITSYS") else ""
    libList = [""]
    if "CMSSW_VERSION" in os.environ:
        libList += ["RooFitCore", "RooFit", "RooStats"]

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

    os.system("cd %s; make -s drive" % dir)


def compile_make(dir="cpp"):
    os.system("cd %s; make -s" % dir)


def compile():
    if __root6:
        compile_make()
    else:
        compile_aclic()


def load(dir="cpp"):
    r.gSystem.AddDynamicPath(dir)
    libs = ["StandardHypoTestInvDemo_cxx"]
    if __root6:
        libs.append("PDFs")
    else:
        libs += ["Gaussian_cxx", "Lognormal_cxx", "Poisson_cxx"]
    for name in libs:
        r.gSystem.Load("%s.so" % name)


def load_and_test():
    load()
    x = r.Poisson
    x = r.Gaussian
    x = r.Lognormal
