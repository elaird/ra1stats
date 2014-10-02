import os
import configuration.directories

def submitBatchJob(jobCmd, indexDict, subScript, jobScript, condorTemplate, jobScriptFileName_format=None, doCopy=False) :
    if jobScriptFileName_format == None :
        jobScriptFileName_format = "%(base)s/%(tag)s/%(sample)s/job%(iSlice)d.sh"
    jobScriptFileName = jobScriptFileName_format%indexDict
    jobScriptDir = jobScriptFileName[:jobScriptFileName.rfind('/')]
    if not os.path.isdir(jobScriptDir): os.system("mkdir -p %s"%jobScriptDir)
    if doCopy :
        os.system("cp -p "+jobScript+" "+jobScriptFileName)
        os.system("chmod +x "+jobScriptFileName)
    mode = "a" if doCopy else "w"
    jobScriptFileName = "%s/%s" % (os.environ["PWD"], jobScriptFileName)
    #print jobScriptFileName
    with open(jobScriptFileName, mode) as file :
        print >>file
        for item in ["PYTHONPATH", "LD_LIBRARY_PATH"] :
            value = os.environ[item]
            value = value.replace('";','"') # hack for fnal batch; perhaps there is a more elegant solution
            print >>file, "export %s=%s"%(item, value)
        print >>file, "cd "+os.environ["PWD"]
        print >>file, jobCmd

    if os.path.exists(condorTemplate) :
        condorFileName = jobScriptFileName.replace(".sh",".condor")
        os.system("cat %s | sed s@JOBFLAG@%s@g > %s"%(condorTemplate, jobScriptFileName, condorFileName))
        # outdir = "./ra1stats/"+configuration.directories.job()
        # os.system("cat %s | sed s@JOBFLAG@%s@g | sed s@OUTFLAG@%s@g | sed s@INFLAG@%s@g > %s"%(condorTemplate, jobScriptFileName, outdir, os.environ["PWD"] , condorFileName)) ###this comment is kept because it is a slower method in LPC LL
        arg = condorFileName
    else :
        arg = jobScriptFileName
    subCmd = "%s %s" % (subScript, arg)
    #print subCmd
    os.chdir(os.environ["PWD"]+"/"+configuration.directories.job())
    os.system(subCmd)
    os.chdir(os.environ["PWD"])
