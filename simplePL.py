import ROOT as r
import baseOneBin

class simplePL(baseOneBin.baseOneBin) :

    def __init__(self, inputData ) :
        super(simplePL,self).__init__(inputData)

        self.data = self.setup1BinLikelihood()
        self.model = self.modelConfiguration()
    
    def setup1BinLikelihood(self) :
        self.wspace.factory("Poisson::select_constraint(n_selected,constituents)")
        self.wspace.factory("PROD::total_model(select_constraint,shared_constraints)")

        self.wspace.defineSet("observe","")
        emptyData = r.RooDataSet("data", "empty", self.wspace.set("observe"))
        return emptyData
    
    def modelConfiguration(self)  :
        model = self.baseModel("Model")
        model.SetPdf(self.wspace.pdf("total_model"))
        return model

    def upperLimit(self, confidenceLevel) :
        self.wspace.Print()
        
        plc = r.RooStats.ProfileLikelihoodCalculator(self.data, self.model)
        plc.SetConfidenceLevel(confidenceLevel)
        
        plInt = plc.GetInterval()
        return plInt.UpperLimit(self.wspace.var(self.interest))
