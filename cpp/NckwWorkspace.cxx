// Run the Asymptotic Calculation for Median + Bands on standard CombinedLimit workspace
// Based of this tutorial https://twiki.cern.ch/twiki/bin/view/RooStats/RooStatsTutorials

#include "TROOT.h"
#include "TSystem.h"
#include "TFile.h"
#include "TTree.h"

#include "RooDataSet.h"
#include "RooWorkspace.h"
#include "RooRealVar.h"
#include "RooStats/ModelConfig.h"
#include "RooStats/AsymptoticCalculator.h"
#include "RooStats/ToyMCSampler.h"
#include "RooStats/ProfileLikelihoodTestStat.h"
#include "RooStats/HypoTestInverter.h"
#include "RooStats/HypoTestInverterResult.h"


namespace RooStats { 
    void asROOT( RooWorkspace* w ) {
    
        double npoints = 20;
        double rMin =0;
        double rMax =5;
  
        //RooWorkspace *w =(RooWorkspace *) _file0->Get("Workspace");
        std::cout << "getting data" << std::endl;
        RooDataSet *data = (RooDataSet*)w->data("dataName");
        std::cout << data << std::endl;
        RooStats::ModelConfig *bModel =(RooStats::ModelConfig*) w->genobj("");
        RooStats::ModelConfig *sbModel =(RooStats::ModelConfig*) w->genobj("modelConfig");

        if (!bModel || bModel == sbModel) {
            Info("NckwWorkspace","The background model %s does not exist","");
            Info("NckwWorkspace","Copy it from ModelConfig %s and set POI to zero","modelConfig");
            bModel = (ModelConfig*) sbModel->Clone();
            bModel->SetName(TString("modelConfig")+TString("_with_poi_0"));      
            RooRealVar * var = dynamic_cast<RooRealVar*>(bModel->GetParametersOfInterest()->first());
            if (!var) return;
            double oldval = var->getVal();
            var->setVal(0);
            bModel->SetSnapshot( RooArgSet(*var)  );
            var->setVal(oldval);
        }

        RooRealVar *poi = (RooRealVar*)sbModel->GetParametersOfInterest()->first();
        sbModel->SetSnapshot(*poi);
        double oldval = poi->getVal();
        poi->setVal(0); bModel->SetSnapshot(*poi);
        poi->setVal(oldval);
  
  
        // Set up asymptotic calculator
        RooStats::AsymptoticCalculator * ac = new RooStats::AsymptoticCalculator(*data, *bModel, *sbModel);
        RooStats::AsymptoticCalculator::SetPrintLevel(-1);
        ac->SetOneSided(true);
        RooStats::HypoTestInverter calc(*ac);
        calc.UseCLs(true);
  
        //Do i need the toy mc sampler? probably needed only for actually running with the toys right?
        //RooStats::ToyMCSampler *toymcs = (RooStats::ToyMCSampler*)calc.GetHypoTestCalculator()->GetTestStatSampler();
        //RooStats::ProfileLikelihoodTestStat profll(*sbModel->GetPdf());
        //profll.SetOneSided(true);
        //toymcs->SetTestStatistic(&profll);
        // --------
  
        calc.SetFixedScan(npoints,rMin,rMax);
        RooStats::HypoTestInverterResult * r = calc.GetInterval();
  
        // Easy as that --> Results output in same format as combine
        double upperLimit = r->UpperLimit();
        double ulError = r->UpperLimitEstimatedError();

        std::cout << "The computed upper limit is: " << upperLimit << " +/- " << ulError << std::endl;
        std::cout << std::endl;
        std::cout << " expected limit (median) " << r->GetExpectedUpperLimit(0) << std::endl;
        std::cout << " expected limit (-1 sig) " << r->GetExpectedUpperLimit(-1) << std::endl;
        std::cout << " expected limit (+1 sig) " << r->GetExpectedUpperLimit(1) << std::endl;
        std::cout << " expected limit (-2 sig) " << r->GetExpectedUpperLimit(-2) << std::endl;
        std::cout << " expected limit (+2 sig) " << r->GetExpectedUpperLimit(2) << std::endl;
  
        delete ac;
     }
}
