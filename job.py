#!/usr/bin/env python
import sys
import ROOT as r
import configuration as conf

def pwd() :
    return sys.argv[1]

def fileName() :
    return sys.argv[2]

def funcName() :
    return fileName().split("/")[-1].replace(".C","")

def points() :
    return [(int(sys.argv[i]), int(sys.argv[i+1])) for i in range(3, len(sys.argv), 2)]

r.gROOT.LoadMacro("%s+"%fileName())

for point in points() :
    getattr(r, funcName())(conf.plotFileName(*point),
                           conf.workspaceFileName(*point),

                           conf.mSuGra_FileSignal(),
                           conf.mSuGra_FileMuonControl(),
                           conf.mSuGra_DirMuonControl(),
                           conf.mSuGra_HistMuonControl(),
                           conf.mSuGra_FileSys05(),
                           conf.mSuGra_FileSys2(),

                           conf.lumi(),
                           *point)
