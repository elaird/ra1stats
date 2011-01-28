#!/usr/bin/env python

def sourceFile() :
    return "Lepton.C"

def tag(m0, m12) :
    return "m0_%d_m12_%d"%(m0, m12)

def plotStem() :
    return "Significance_35pb"

def plotFileName(m0, m12) :
    return "%s_%s.root"%(plotStem(), tag(m0, m12))

def workspaceStem() :
    return "Combine"

def workspaceFileName(m0, m12) :
    return "%s_%s.root"%(workspaceStem(), tag(m0, m12))

def logFileName(iSlice) :
    return "Significance_job_%d.log"%iSlice
