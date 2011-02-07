import ROOT as r

class simpleCLs(object) :

    def __init__(self, inputData ) :
        self.translateInputData(inputData)
        
        r.RooRandom.randomGenerator().SetSeed(inputData["seed"])
        self.wspace = r.RooWorkspace("Workspace")
        self.data = self.setup1BinCLs()
        self.b_model = self.modelConfiguration("B Model",0)
    
    def translateInputData(self,iD) :
        self.interest = "susy"
        self.constituents = ["zinv","ttw"]

        self.values = { 'n_selected'      : sum(iD['n_signal']),
                        'n_muon'          : sum(iD['n_muoncontrol']),
                        'n_photon'        : sum(iD['n_photoncontrol']),
                        'mc_tau_mu'       : sum(iD['mc_muoncontrol'])   / sum(iD['mc_ttW']),
                        'mc_tau_ph'       : sum(iD['mc_photoncontrol']) / sum(iD['mc_Zinv']),
                        'sigma_R_susy_eff': iD['sigma_SigEff']}
        self.values['sigma_tau_ph'] = self.values['mc_tau_ph'] * iD['sigma_Zinv']
        self.values['sigma_tau_mu'] = self.values['mc_tau_mu'] * iD['sigma_ttW']

        self.params = {'R_susy_eff' : 1.,
                       'tau_mu'     : self.values['mc_tau_mu'],
                       'tau_ph'     : self.values['mc_tau_ph']}
        return
    
    def wimport(self, name = None, value = None, lower = None, upper = None) :
        assert name and value!=None
        assert (lower==None==upper) or (lower!=None!=upper)
        if lower==upper==None : getattr(self.wspace, "import")(r.RooRealVar(name, name, value))
        else :                  getattr(self.wspace, "import")(r.RooRealVar(name, name, value, lower, upper))
        return

    def setup1BinCLs(self) :
        
        # Import vars into the workspace
        nsel = self.values["n_selected"]
        self.wimport(self.interest, 0.1*nsel, 1e-5, 3*nsel)
        for name in self.constituents :           self.wimport(name, 0.5*nsel, 1e-2, 5*nsel)
        for name,val in self.params.iteritems() : self.wimport(name, val, 0.01*val, 100*val)
        for pair in self.values.iteritems():      self.wimport(*pair)

        # Construct the likelihood constraints
        self.wspace.factory("ExtendPdf::selected(Uniform::f(m[0,1]),sum::constituents(%s))" % ','.join(["prod::susy_yeild(susy,R_susy_eff)"]+
                                                                                                       self.constituents))
        self.wspace.factory("Poisson::photon_constraint(n_photon,prod::photons(zinv,tau_ph))")
        self.wspace.factory("Poisson::muon_constraint(n_muon,prod::muons(ttw,tau_mu))")
        self.wspace.factory("Gaussian::tau_mu_constraint(mc_tau_mu,tau_mu,sigma_tau_mu)")
        self.wspace.factory("Gaussian::tau_ph_constraint(mc_tau_ph,tau_ph,sigma_tau_ph)")
        self.wspace.factory("Gaussian::R_susy_eff_constraint(1.,R_susy_eff,sigma_R_susy_eff)")
        
        self.wspace.factory("PROD::constraints(%s)" % ','.join(["%s_constraint"%s for s in ["photon","muon",
                                                                                            "tau_mu","tau_ph","R_susy_eff"]]))
        self.wspace.defineSet("interest",self.interest)
        self.wspace.defineSet("nuisance",','.join(self.params.keys()+self.constituents))
        self.wspace.defineSet("observe","m")
        data = self.wspace.pdf("selected").generate(self.wspace.set("observe"),nsel)
        return data
    
    def modelConfiguration(self,name,n_susy) :
        model = r.RooStats.ModelConfig(name,self.wspace)
        model.SetPdf(self.wspace.pdf("selected"))
        model.SetParametersOfInterest(self.wspace.set("interest"))
        model.SetNuisanceParameters(self.wspace.set("nuisance"))
        model.SetObservables(self.wspace.set("observe"))
        self.wspace.var(self.interest).setVal(n_susy)
        model.SetSnapshot(self.wspace.set("interest"))
        return model

    def CLsHypoTest(self, n_susy) :
        sb_model = self.modelConfiguration("S+B Model",n_susy)

        hc = r.RooStats.HybridCalculator(self.data, sb_model, self.b_model)
        hc.ForcePriorNuisanceAlt(self.wspace.pdf("constraints"))
        hc.ForcePriorNuisanceNull(self.wspace.pdf("constraints"))

        hc.GetTestStatSampler().SetTestStatistic( r.RooStats.NumEventsTestStat(self.wspace.pdf("selected")) )
        toys = int(3e3)
        hc.SetToys(toys,toys)
        
        return hc.GetHypoTest() # This is the heavy calculation
