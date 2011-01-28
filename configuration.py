#!/usr/bin/env python

def testPointsOnly() : return True

def sourceFile() : return "Lepton.C"

def doBayesian() : return False
def doFeldmanCousins() : return False
def doMCMC() : return False

#name for m0-m12 plane for event yields in signal-like region
def mSuGra_FileSignal() : return "AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_nlo.root"

#name for m0-m12 plane for event yields in the muon control region
def mSuGra_FileMuonControl() : return "AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_muon.root"
def mSuGra_DirMuonControl() : return "mSuGraScan_350"
def mSuGra_HistMuonControl() : return "m0_m12_0"

#name for m0-m12 plane for event yields with modified factorization and renormalization scale 0.5 down
def mSuGra_FileSys05() : return "AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_sys05.root"

#name for m0-m12 plane for event yields with modified factorization and renormalization scale 2 up
def mSuGra_FileSys2() : return "AK5Calo_PhysicsProcesses_mSUGRA_tanbeta3Fall10v1_sys2.root"

#/pb
def lumi() : return 35

#output name options
def outputDir() : return "output"
def logDir() : return "log"
def tag(m0, m12) : return "m0_%d_m12_%d"%(m0, m12)

def plotStem() : return "%s/Significance_%spb"%(outputDir(), lumi())
def plotFileName(m0, m12) : return "%s_%s.root"%(plotStem(), tag(m0, m12))

def workspaceStem() : return "%s/Combine"%outputDir()
def workspaceFileName(m0, m12) : return "%s_%s.root"%(workspaceStem(), tag(m0, m12))
def writeWorkspaceFile() : return False

def logStem() : return "%s/job"%logDir()
def logFileName(iSlice) : return "%s_%d.log"%(logStem(), iSlice)
