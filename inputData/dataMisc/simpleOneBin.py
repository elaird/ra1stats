from inputData import syst
from data import data

class data_simple(data) :
    """one bin test data"""
    
    def _fill(self) :
        self._observations = {
            "nSimple": (9.0,),
            }

        self._mcExpectationsBeforeTrigger = {
            "mcSimple": (10.0,),
            }




        self._htBinLowerEdges = (875.0, )
        self._htMaxForPlot = 975.0
        
        self._mergeBins = None
        self._constantMcRatioAfterHere = ( 1, )

        self._htMeans = ( 9.188e+02, )
        self._lumi = {
            "simple": 1.0
            }

        self._triggerEfficiencies = {
            "simple" : (1.0,),
            }

        for item in ["mcStatError", "purities", "mcExtraBeforeTrigger"] :
            setattr(self, "_%s"%item, {})

        self._systBins = {
            "sigmaLumiLike": [0],
            }
        
        data._fixedParameters = {
            "sigmaLumiLike": (0.001,),
            }
