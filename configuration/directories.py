import os


def job():
    return "jobIO"


def log():
    return "log"


def plot():
    return "plots"


def points():
    return "points"


def mergedFile():
    return "ra1r/scan"


def eff():
    return "ra1e"


def xs():
    return "xs"


def pickledFileName(name, xBin, yBin, zBin, out=False):
    stem = "%s_%d_%d_%d.pickled" % (name, xBin, yBin, zBin)
    if out:
        d = os.environ.get("_CONDOR_SCRATCH_DIR", job())  # for FNAL worker nodes
        return "%s/%s.out" % (d, stem)
    else:
        return "%s/%s.in" % (job(), stem)

