import ROOT as r

class baseOneBin(object) :

    def __init__(self, inputData ) :
        self.translateInputData(inputData)
        r.RooRandom.randomGenerator().SetSeed(inputData["seed"])
        self.wspace = r.RooWorkspace("Workspace")
        self.buildShared()
    
    def translateInputData(self,iD) :
        self.interest = "susy"
        self.constituents = ["zinv","ttw"]

        self.values = { 'n_selected'      : sum(iD['n_signal']),
                        'n_muon'          : sum(iD['n_muoncontrol']),
                        'n_photon'        : sum(iD['n_photoncontrol']),
                        'mc_tau_mu'       : sum(iD['mc_muoncontrol'])   / sum(iD['mc_ttW']),
                        'mc_tau_ph'       : sum(iD['mc_photoncontrol']) / sum(iD['mc_Zinv']),
                        'sigma_R_susy_eff': iD['sigma_SigEff'],
                        'R_susy_muons'        : 0.0}
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

    def buildShared(self) :
        
        # Import vars into the workspace
        nsel = self.values["n_selected"]
        self.wimport(self.interest, 0.1*nsel, 1e-5, 3*nsel)
        for name in self.constituents :           self.wimport(name, 0.5*nsel, 1e-2, 5*nsel)
        for name,val in self.params.iteritems() : self.wimport(name, val, 0.01*val, 100*val)
        for pair in self.values.iteritems():      self.wimport(*pair)

        # Sets
        self.wspace.defineSet("interest",self.interest)
        self.wspace.defineSet("nuisance",','.join(self.params.keys()+self.constituents))
        
        # Functions
        self.wspace.factory("sum::constituents(%s)" % ','.join(["prod::susy_yeild(susy,R_susy_eff)"]+self.constituents))
        
        # Constraints
        self.wspace.factory("Gaussian::tau_mu_constraint(mc_tau_mu,tau_mu,sigma_tau_mu)")
        self.wspace.factory("Gaussian::tau_ph_constraint(mc_tau_ph,tau_ph,sigma_tau_ph)")
        self.wspace.factory("Gaussian::R_susy_eff_constraint(1.,R_susy_eff,sigma_R_susy_eff)")
        self.wspace.factory("Poisson::photon_constraint(n_photon,prod::photons(zinv,tau_ph))")
        self.wspace.factory("Poisson::muon_constraint(n_muon,%s)"%("sum::contaminatedMu(%s,%s)"%("prod::muons(ttw,tau_mu)",
                                                                                                 "prod::susy_muons(susy,R_susy_muons)")))
        
        self.shared_constraints = ','.join(["%s_constraint"%s for s in ["tau_mu","tau_ph","R_susy_eff","photon","muon"]])
        self.wspace.factory("PROD::shared_constraints(%s)"%self.shared_constraints)
        return
    
    def baseModel(self,name) :
        model = r.RooStats.ModelConfig(name,self.wspace)
        model.SetParametersOfInterest(self.wspace.set("interest"))
        model.SetNuisanceParameters(self.wspace.set("nuisance"))
        return model

    def setValue(name,value) : self.wspace.var(name).setVal(value)
    
