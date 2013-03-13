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


def pickledFileName(xBin, yBin, zBin):
    return "%s/m0_%d_m12_%d_mZ_%d.pickled" % (job(), xBin, yBin, zBin)
