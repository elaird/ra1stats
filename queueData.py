import configuration
all_queues = {
    "short"  :  { "ncores" : 336, "factor" :  1., },
    "medium" :  { "ncores" : 116, "factor" :  6., },
    "long"   :  { "ncores" :  52, "factor" : 72., },
}

qData = {}
for queue_name in configuration.switches()["queueSelection"] :
    qData[queue_name] = all_queues.get(queue_name,{"ncores":0, "factor": 0.})
