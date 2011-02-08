import ROOT as r
import baseOneBin

class simpleCLs(baseOneBin.baseOneBin) :
    
    def __init__(self, inputData ) :
        super(simpleCLs,self).__init__(inputData)
        
        self.data = self.setup1BinCLs()
        self.b_model = self.modelConfiguration("B Model",0)
        self.sb_model = self.modelConfiguration("S+B Model",0)
    
    def setup1BinCLs(self) :
        self.wspace.factory("ExtendPdf::selected(Uniform::f(m[0,1]),constituents)")
        self.wspace.defineSet("observe","m")
        data = self.wspace.pdf("selected").generate(self.wspace.set("observe"),self.values['n_selected'])
        return data
    
    def modelConfiguration(self,name,n_susy) :
        model = self.baseModel(name)
        model.SetPdf(self.wspace.pdf("selected"))
        model.SetObservables(self.wspace.set("observe"))
        return model

    def fix_nsusy(self,model,nsusy) :
        self.wspace.var(self.interest).setVal(nsusy)
        model.SetSnapshot(self.wspace.set("interest"))

    def CLsHypoTest(self, n_susy) :
        self.fix_nsusy(self.b_model,0)
        self.fix_nsusy(self.sb_model,n_susy)
                
        hc = r.RooStats.HybridCalculator(self.data, self.sb_model, self.b_model)
        hc.ForcePriorNuisanceAlt(self.wspace.pdf("shared_constraints"))
        hc.ForcePriorNuisanceNull(self.wspace.pdf("shared_constraints"))

        hc.GetTestStatSampler().SetTestStatistic( r.RooStats.NumEventsTestStat(self.wspace.pdf("selected")) )
        toys = int(3e3)
        hc.SetToys(toys,toys)
        
        return hc.GetHypoTest() # This is the heavy calculation
