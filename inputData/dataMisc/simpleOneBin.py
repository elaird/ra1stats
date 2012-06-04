from inputData import syst
from data import data,scaled,excl

class data_simple(data) :
    """one bin test data"""
    
    def _fill(self) :
        self._htBinLowerEdges = (875.0, )
        self._htMaxForPlot = 975.0
        
        self._mergeBins = None
        self._constantMcRatioAfterHere = ( 1, )

        self._htMeans = ( 9.188e+02, )
        self._lumi = {
            "simple":     4650.,
            }
        self._observations = {
            "nSimple": (6.0,),
            }

        self._triggerEfficiencies = {
            "simple" : (1.0,),
            }

        self._mcExpectationsBeforeTrigger = {
            "mcSimple": (4.0,),
            }

        for item in ["mcStatError", "purities", "mcExtraBeforeTrigger"] :
            setattr(self, "_%s"%item, {})

        self._systBins = {
            "sigmaLumiLike": [0],
            }
        
        data._fixedParameters = {
            "sigmaLumiLike": (0.15,),
            }
