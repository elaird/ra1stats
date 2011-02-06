#include "TH2F.h"
#include "TH3F.h"
#include "TFile.h"
#include "TDirectory.h"
#include "TString.h"

TH2F* yieldPlot(const std::string& mSuGraFile,const std::string& mSuGraDir,const std::string& mSuGraHist) {
  //read In mSuGra Histo
  TFile* f = new TFile(mSuGraFile.c_str());
  TDirectory* dir = (TDirectory*)f->Get(mSuGraDir.c_str());
  
  TH2F* hnev = (TH2F*)dir->Get(mSuGraHist.c_str());

  return hnev;
}

TH3F* yieldPlot_3d(TString& mSuGraFile,TString& mSuGraDir,TString& mSuGraHist) {
  //read In mSuGra Histo
  TFile* f = new TFile(mSuGraFile);
  f->ls();
  TDirectory* dir = (TDirectory*)f->Get(mSuGraDir);
  dir->ls();
  TH3F* hnev = (TH3F*)dir->Get(mSuGraHist);
  hnev->Print();

  return hnev;
}

//a little plotting routine to calculate the NLO cross-section
TH2F* sysPlot(TString& mSuGraFile, TString& mSuGraDir1, TString& mSuGraFile_before, TString& mSuGraDir_before) {
  //read In mSuGra Histo
  TFile* f = new TFile(mSuGraFile);
  TFile* f_before = new TFile(mSuGraFile_before);

  f->ls();
  TDirectory* dir = (TDirectory*)f->Get(mSuGraDir1);
  TDirectory* dir2 = (TDirectory*)f_before->Get(mSuGraDir_before);

  dir2->ls();

  cout << " in " << endl;
  
  TH2F* gg = (TH2F*)dir->Get("m0_m12_gg_0");
  cout << " after gg1 " << endl;
  TH2F* gg_noweight = (TH2F*)dir2->Get("m0_m12_gg_5");

  cout << " after gg " << endl;
  TH2F* sb = (TH2F*)dir->Get("m0_m12_sb_0");
  TH2F* sb_noweight = (TH2F*)dir2->Get("m0_m12_sb_5");
  TH2F* ss = (TH2F*)dir->Get("m0_m12_ss_0");
  TH2F* ss_noweight = (TH2F*)dir2->Get("m0_m12_ss_5");
  TH2F* sg = (TH2F*)dir->Get("m0_m12_sg_0");
  TH2F* sg_noweight = (TH2F*)dir2->Get("m0_m12_sg_5");
  TH2F* ll = (TH2F*)dir->Get("m0_m12_ll_0");
  TH2F* ll_noweight = (TH2F*)dir2->Get("m0_m12_ll_5");
  TH2F* nn = (TH2F*)dir->Get("m0_m12_nn_0");
  TH2F* nn_noweight = (TH2F*)dir2->Get("m0_m12_nn_5");
  TH2F* ns = (TH2F*)dir->Get("m0_m12_ns_0");
  TH2F* ns_noweight = (TH2F*)dir2->Get("m0_m12_ns_5");
  //TH2F* ng = (TH2F*)dir2->Get("m0_mg12_ng_0");                                                               
  //TH2F* ng_noweight = (TH2F*)dir->Get("m0_m12_ng_5");
  TH2F* bb = (TH2F*)dir->Get("m0_m12_bb_0");
  TH2F* bb_noweight = (TH2F*)dir2->Get("m0_m12_bb_5");
  TH2F* tb = (TH2F*)dir->Get("m0_m12_tb_0");
  TH2F* tb_noweight = (TH2F*)dir2->Get("m0_m12_tb_5");

  cout << " Here " << endl;
  
  gg->Divide(gg_noweight);
  sb->Divide(sb_noweight);
  ss->Divide(ss_noweight);
  sg->Divide(sg_noweight);
  ll->Divide(ll_noweight);
  nn->Divide(nn_noweight);
  //ng->Divide(ng_noweight);
  bb->Divide(bb_noweight);
  tb->Divide(tb_noweight);
  ns->Divide(ns_noweight);

  TH2F* all = (TH2F*)gg->Clone();
  all->Add(sb);
  all->Add(ss);
  all->Add(sg);
  all->Add(ll);
  all->Add(nn);
  //all->Add(ng);
  all->Add(bb);
  all->Add(tb);
  all->Add(ns);

  all->Scale(100);
  
  
 

  return all;
}


TH2F *histoWithBinning(std::string& mSuGraFile_muoncontrol,
		       std::string& mSuGraDir_muoncontrol,
		       std::string& mSuGraHist_muoncontrol
		       ) {
  TFile f(mSuGraFile_muoncontrol.c_str());
  TH2F *h = (TH2F*)f.Get((mSuGraDir_muoncontrol+"/"+mSuGraHist_muoncontrol).c_str());
  TString name = h->GetName();
  name += "_clone";
  TH2F *g = (TH2F*)h->Clone(name);
  g->SetDirectory(0);
  f.Close();
  return g;
}


void writeExclusionLimitPlot(TH2F *exampleHisto, std::string& outputPlotFileName, int m0, int m12, bool isInInterval) {
  TFile output(outputPlotFileName.c_str(), "RECREATE");
  if (output.IsZombie()) std::cout << " zombie alarm output is a zombie " << std::endl;

  if (!exampleHisto) {
    std::cout << "exampleHisto is NULL" << std::endl;
    return;
  }

  TH2F *exclusionLimit = (TH2F*)exampleHisto->Clone("ExclusionLimit");
  exclusionLimit->SetTitle("ExclusionLimit;m_{0} (GeV);m_{1/2} (GeV)");
  exclusionLimit->Reset();
  exclusionLimit->SetBinContent(m0, m12, 2.0*isInInterval - 1.0);
  exclusionLimit->Write();

  output.cd();
  output.Close();
}

void checkMap(int nInitial, int nFinal) {
  if (nInitial!=nFinal) std::cerr << "ERROR: nInitial = " << nInitial << "; nFinal = " << nFinal << std::endl;  
}







