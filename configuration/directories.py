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

def pickledFileName(name, xBin, yBin, zBin):
	return "%s/%s_%d_%d_%d.pickled" % (job(), name, xBin, yBin, zBin)