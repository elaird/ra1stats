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
    HypoTestInverterResult* 
    asROOT( RooWorkspace* w, const char * modelSBName, const char * modelBName,
            const char * dataName, int type, int testStatType, bool useCLs,
            int npoints, double poimin, double poimax, int ntoys,
            bool useNumberCounting = false, const char * nuisPriorName = 0) {
            // nuisPrioName only used for calc type = 1
    
        RooDataSet *data = (RooDataSet*)w->data(dataName);
        RooStats::ModelConfig *bModel =(RooStats::ModelConfig*) w->genobj(modelBName);
        RooStats::ModelConfig *sbModel =(RooStats::ModelConfig*) w->genobj(modelSBName);

        if (!bModel || bModel == sbModel) {
            Info("NckwWorkspace","The background model %s does not exist","");
            Info("NckwWorkspace","Copy it from ModelConfig %s and set POI to zero",modelSBName);
            bModel = (ModelConfig*) sbModel->Clone();
            bModel->SetName(TString(modelSBName)+TString("_with_poi_0"));
            RooRealVar * var = dynamic_cast<RooRealVar*>(bModel->GetParametersOfInterest()->first());
            if (!var) return NULL;
            double oldval = var->getVal();
            var->setVal(0);
            bModel->SetSnapshot( RooArgSet(*var)  );
            var->setVal(oldval);
        }

        RooRealVar *poi = (RooRealVar*)sbModel->GetParametersOfInterest()->first();
        sbModel->SetSnapshot(*poi);
        double oldval = poi->getVal();
        poi->setVal(0);
        bModel->SetSnapshot(*poi);
        poi->setVal(oldval);
  
  
        // Set up asymptotic calculator
        RooStats::AsymptoticCalculator * ac = new RooStats::AsymptoticCalculator(*data, *bModel, *sbModel);
        RooStats::AsymptoticCalculator::SetPrintLevel(-1);
        ac->SetOneSided(true);
        RooStats::HypoTestInverter calc(*ac);
        calc.UseCLs(useCLs);
  
        //Do i need the toy mc sampler? probably needed only for actually running with the toys right?
        //RooStats::ToyMCSampler *toymcs = (RooStats::ToyMCSampler*)calc.GetHypoTestCalculator()->GetTestStatSampler();
        //RooStats::ProfileLikelihoodTestStat profll(*sbModel->GetPdf());
        //profll.SetOneSided(true);
        //toymcs->SetTestStatistic(&profll);
        //
        //   from StandardHypoTestInvDemo
        // ToyMCSampler *toymcs = (ToyMCSampler*)hc->GetTestStatSampler();
        // if (toymcs) { 
        //    if (useNumberCounting) toymcs->SetNEventsPerToy(1);
        //    toymcs->SetTestStatistic(testStat);
        //  
        //    if (data->isWeighted() && !mGenerateBinned) { 
        //       Info("StandardHypoTestInvDemo","Data set is weighted, nentries = %d and sum of weights = %8.1f but toy generation is unbinned - it would be faster to set mGenerateBinned to true\n",data->numEntries(), data->sumEntries());
        //    }
        //    toymcs->SetGenerateBinned(mGenerateBinned);
        //
        //    toymcs->SetUseMultiGen(mOptimize);
        //  
        //    if (mGenerateBinned &&  sbModel->GetObservables()->getSize() > 2) { 
        //       Warning("StandardHypoTestInvDemo","generate binned is activated but the number of ovservable is %d. Too much memory could be needed for allocating all the bins",sbModel->GetObservables()->getSize() );
        //    }

        //    // set the random seed if needed
        //    if (mRandomSeed >= 0) RooRandom::randomGenerator()->SetSeed(mRandomSeed); 
        //  
        // }
        // --------
  
        calc.SetFixedScan(npoints,poimin,poimax);
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
        return r;
     }
}
