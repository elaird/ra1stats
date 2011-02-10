import ROOT as r
import baseOneBin

class simpleFC(baseOneBin.baseOneBin) :

    def __init__(self, inputData ) :
        super(simpleFC,self).__init__(inputData)

        self.data = self.setup1BinLikelihood()
        self.model = self.modelConfiguration()
    
    def setup1BinLikelihood(self) :
        self.wspace.factory("Poisson::select_constraint(n_selected,constituents)")
        self.wspace.factory("PROD::total_model(select_constraint,shared_constraints)")

        self.wspace.defineSet("observe",','.join(self.counts))
        #data = r.RooDataSet("data", "counts", self.wspace.set("observe"))
        #return data

        lolArgSet = self.wspace.set("observe")
        newSet = r.RooArgSet(self.wspace.set("observe"))
        for name,val in self.counts.iteritems() :
            newSet.setRealValue(name,val)
            
        data = r.RooDataSet("BurtTestData", "title", lolArgSet)
        data.add(lolArgSet)
        getattr(self.wspace, "import")(data)
        return data
    
    def modelConfiguration(self)  :
        model = self.baseModel("Model")
        model.SetPdf(self.wspace.pdf("total_model"))
        getattr(self.wspace,"import")(model)
        return model

    def upperLimit(self, confidenceLevel) :
        
        fc = r.RooStats.FeldmanCousins(self.data, self.model)
        fc.SetConfidenceLevel(confidenceLevel)
        fc.FluctuateNumDataEntries(False)
        fc.UseAdaptiveSampling(True)
        fc.AdditionalNToysFactor(4)
        fc.SetNBins(40)
    
        self.wspace.Print()
        interval = fc.GetInterval()
        return interval.UpperLimit(self.wspace.var(self.interest))
