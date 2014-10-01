import os

def job():
	return "jobIO"

def workingNode():
	return os.environ["_CONDOR_SCRATCH_DIR"] ##CONDOR_SCRATCH_DIR option is for running at LPC

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

def pickledFileName(name, xBin, yBin, zBin):
	return "%s/%s_%d_%d_%d.pickled" % (job(), name, xBin, yBin, zBin)

def FNALpickledFileName(name, xBin, yBin, zBin):
	return "%s/%s_%d_%d_%d.pickled" % (workingNode(), name, xBin, yBin, zBin)
	##To Ted: Can't use os.getenv() in job() because the directories of pickledin files will mess up, LL