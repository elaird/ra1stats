import ROOT as r

class simplePL(object) :

    def __init__(self, inputData ) :
        self.translateInputData(inputData)
        
        r.RooRandom.randomGenerator().SetSeed(inputData["seed"])
        self.wspace = r.RooWorkspace("Workspace")
        self.data = self.setup1BinLikelihood()
        self.model = self.modelConfiguration()
    
    def translateInputData(self,iD) :
        self.interest = "susy"
        self.constituents = ["zinv","ttw"]

        self.values = { 'n_selected'    : sum(iD['n_signal']),
                        'n_muon'        : sum(iD['n_muoncontrol']),
                        'n_photon'      : sum(iD['n_photoncontrol']),
                        'mc_tau_mu'     : sum(iD['mc_muoncontrol'])   / sum(iD['mc_ttW']),
                        'mc_tau_ph'     : sum(iD['mc_photoncontrol']) / sum(iD['mc_Zinv']),
                        'sigma_susy_eff': iD['sigma_SigEff']}
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

    def setup1BinLikelihood(self) :
        
        # Import vars into the workspace
        nsel = self.values["n_selected"]
        self.wimport(self.interest, 0.1*nsel, 1e-5, 3*nsel)
        for name in self.constituents :           self.wimport(name, 0.5*nsel, 1e-2, 5*nsel)
        for name,val in self.params.iteritems() : self.wimport(name, val, 0.01*val, 100*val)
        for pair in self.values.iteritems():      self.wimport(*pair)

        self.wspace.defineSet("interest",self.interest)
        self.wspace.defineSet("nuisance",','.join(self.params.keys()+self.constituents))
        self.wspace.defineSet("observe","")
        emptyData = r.RooDataSet("data", "empty", self.wspace.set("observe"))

        # Construct the likelihood constraints
        self.wspace.factory("Poisson::select_constraint(n_selected,sum::constituents(%s))" % ','.join(["prod::susy_yeild(susy,R_susy_eff)"]+
                                                                                                      self.constituents))
        self.wspace.factory("Poisson::photon_constraint(n_photon,prod::photons(zinv,tau_ph))")
        self.wspace.factory("Poisson::muon_constraint(n_muon,prod::muons(ttw,tau_mu))")
        self.wspace.factory("Gaussian::tau_mu_constraint(mc_tau_mu,tau_mu,sigma_tau_mu)")
        self.wspace.factory("Gaussian::tau_ph_constraint(mc_tau_ph,tau_ph,sigma_tau_ph)")
        self.wspace.factory("Gaussian::R_susy_eff_constraint(1.,R_susy_eff,sigma_susy_eff)")
        
        self.wspace.factory("PROD::total_model(%s)" % ','.join(["%s_constraint"%s for s in ["select","photon","muon",
                                                                                            "tau_mu","tau_ph","R_susy_eff"]]))
        return emptyData
    
    def modelConfiguration(self)  :
        model = r.RooStats.ModelConfig("Model")
        model.SetWorkspace(self.wspace)
        model.SetPdf(self.wspace.pdf("total_model"))
        model.SetParametersOfInterest(self.wspace.set("interest"))
        model.SetNuisanceParameters(self.wspace.set("nuisance"))
        getattr(self.wspace,"import")(model)
        return model

    def upperLimit(self, confidenceLevel) :

        plc = r.RooStats.ProfileLikelihoodCalculator(self.data, self.model)
        plc.SetConfidenceLevel(confidenceLevel)
        
        plInt = plc.GetInterval()
        return plInt.UpperLimit(self.wspace.var(self.interest))
