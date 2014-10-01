import os

pwd = os.environ["PWD"]

hostname = os.environ["HOSTNAME"]
if "fnal.gov" in hostname:
    batchHost = "FNAL"
else:
    if "hep.ph.ic.ac.uk" in hostname:
        batchHost = "IC"

icQueues = {"short":  {"ncores": 336, "factor":  1.},
            "medium": {"ncores": 116, "factor":  6.},
            "long":   {"ncores":  52, "factor": 72.},
            }


def qData(selection=["short", "medium", "long"][0:1]):
    out = {}
    for name in selection:
        out[name] = icQueues[name]
    return out


def subCmdFormat():
    return "qsub -o /dev/null -e /dev/null -q hep%s.q"


def envScript():
    return "env.sh"


def nJobsMax():
    return {"IC": 2000, "FNAL": 1000}[batchHost]


def subCmd(icQueue="medium"):
    assert icQueue in icQueues, icQueue
    return {"IC": "qsub -o /dev/null -e /dev/null -q hep%s.q" % icQueue,
            "FNAL": "condor_submit",
            }[batchHost]

def workingDir():
    return {"IC": pwd, "FNAL": pwd}[batchHost]
