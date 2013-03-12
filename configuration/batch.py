batchHost = [ "FNAL", "IC" ][1]

def qData(selection=["short", "medium", "long"][0:1]):
    icQueues = {"short"  :  { "ncores" : 336, "factor" :  1., },
                "medium" :  { "ncores" : 116, "factor" :  6., },
                "long"   :  { "ncores" :  52, "factor" : 72., },
                }

    out = {}
    for name in selection:
        out[name] = icQueues.get(name, {"ncores":0, "factor": 0.})
    return out

def other() :
    return {"subCmdFormat": "qsub -o /dev/null -e /dev/null -q hep%s.q",
            "envScript": "env.sh",
            }

def nJobsMax():
    return {"IC": 2000, "FNAL": 0}[batchHost]

def subCmd(icQueue="medium"):
    assert icQueue in ["short", "medium", "long"], icQueue
    return {"IC": "qsub -o /dev/null -e /dev/null -q hep%s.q" % icQueue,
            "FNAL": "condor_submit",
            }[batchHost]
