#!/usr/bin/env python

def sourceFile() :
    return "Lepton.C"

def tag(m0, m12) :
    return "m0_%d_m12_%d"%(m0, m12)

def plotFileName(m0, m12) :
    return "Significance_35pb_%s.root"%tag(m0, m12)

def workspaceFileName(m0, m12) :
    return "Combine_%s.root"%tag(m0, m12)

def logFileName(iSlice) :
    return "Significance_job_%d.log"%iSlice
