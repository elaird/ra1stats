#include "TH3D.h"
#include "TString.h"
#include "TStyle.h"
#include "TFile.h"
#include <iostream>
#include "TMath.h"
#include "TH2D.h"

using namespace std;

int newpdfUnc(TH3D& diff_effi_mean,TH3D& diff_effi_wplus, TH3D& diff_effi_wminus, int nsets=41,bool nnpdfFlag = 0,TString pdfset ="cteq66"  );

TH3D* getHisto( TString path,
	       TString nameHist,
	       TString nameFile,
	       TString Dirname, 
		int rebin );

void call(){

   // Output file
  TFile* output = new TFile( "Plots_T1.root", "RECREATE" );
  if ( !output || output->IsZombie() ) {  }

  int xBins = 30;
  double xLow =0.;
  double xHigh =1500.;
  int yBins =40;
  double yLow =0.;
  double yHigh =1000.;
  int zBins =40;
  double zLow =0.;
  double zHigh =1000;

  TH3D* final_pdf_mean = new TH3D("final_pdf_mean","Effi_pdf_mean",xBins,xLow,xHigh,yBins,yLow,yHigh,zBins,zLow,zHigh);


  TH3D* final_pdf_error = new TH3D("final_pdf_unc_error","Effi_pdf_unc_wplus",xBins,xLow,xHigh,yBins,yLow,yHigh,zBins,zLow,zHigh);

   TH2D* final_pdf_error_2d = new TH2D("final_pdf_unc_error_2d","Effi_pdf_unc_wplus",xBins,xLow,xHigh,yBins,yLow,yHigh);


  TString pdfset ="cteq66";

  TH3D* diff_effi_mean = new TH3D("Effi_pdf_mean"+pdfset,"Effi_pdf_mean"+pdfset,xBins,xLow,xHigh,yBins,yLow,yHigh,zBins,zLow,zHigh);


  TH3D* diff_effi_wplus = new TH3D("Effi_pdf_unc_wplus"+pdfset,"Effi_pdf_unc_wplus"+pdfset,xBins,xLow,xHigh,yBins,yLow,yHigh,zBins,zLow,zHigh);

  TH3D* diff_effi_wminus = new TH3D("Effi_pdf_unc_wminus"+pdfset,"Effi_pdf_unc_minus"+pdfset,xBins,xLow,xHigh,yBins,yLow,yHigh,zBins,zLow,zHigh);

  pdfset ="NNPDF";

   TH3D* diff_effi_mean_NNPDF = new TH3D("Effi_pdf_mean"+pdfset,"Effi_pdf_mean"+pdfset,xBins,xLow,xHigh,yBins,yLow,yHigh,zBins,zLow,zHigh);


  TH3D* diff_effi_wplus_NNPDF = new TH3D("Effi_pdf_unc_wplus"+pdfset,"Effi_pdf_unc_wplus"+pdfset,xBins,xLow,xHigh,yBins,yLow,yHigh,zBins,zLow,zHigh);

  TH3D* diff_effi_wminus_NNPDF = new TH3D("Effi_pdf_unc_wminus"+pdfset,"Effi_pdf_unc_rel"+pdfset,xBins,xLow,xHigh,yBins,yLow,yHigh,zBins,zLow,zHigh);

   pdfset ="MSTW";

   TH3D* diff_effi_mean_MSTW = new TH3D("Effi_pdf_mean"+pdfset,"Effi_pdf_mean"+pdfset,xBins,xLow,xHigh,yBins,yLow,yHigh,zBins,zLow,zHigh);


  TH3D* diff_effi_wplus_MSTW = new TH3D("Effi_pdf_unc_wplus"+pdfset,"Effi_pdf_unc_wplus"+pdfset,xBins,xLow,xHigh,yBins,yLow,yHigh,zBins,zLow,zHigh);

  TH3D* diff_effi_wminus_MSTW = new TH3D("Effi_pdf_unc_wminus"+pdfset,"Effi_pdf_unc_wminus"+pdfset,xBins,xLow,xHigh,yBins,yLow,yHigh,zBins,zLow,zHigh);



  newpdfUnc(*diff_effi_mean,*diff_effi_wplus,*diff_effi_wminus, 41,0,"cteq66");

  newpdfUnc(*diff_effi_mean_NNPDF,*diff_effi_wplus_NNPDF,*diff_effi_wminus_NNPDF, 101,1,"NNPDF");

  newpdfUnc(*diff_effi_mean_MSTW,*diff_effi_wplus_MSTW,*diff_effi_wminus_MSTW, 41,0,"MSTW");


  Double_t central_value =0;
  Double_t error = 0;

  output->cd();

  for(int m0 = 0; m0 < xBins; m0++){
    
    for(int m12 = 0; m12 < yBins; m12++){

      Double_t x1 = diff_effi_mean->GetBinContent(m0,m12,1);
      Double_t x2 = diff_effi_mean_NNPDF->GetBinContent(m0,m12,1);
      Double_t x3 = diff_effi_mean_MSTW->GetBinContent(m0,m12,1);

      Double_t Ps1 = diff_effi_wplus->GetBinContent(m0,m12,1)/1.645;
      Double_t Ps2 = diff_effi_wplus_NNPDF->GetBinContent(m0,m12,1);
      Double_t Ps3 = diff_effi_wplus_MSTW->GetBinContent(m0,m12,1);

      Double_t Ms1 = diff_effi_wminus->GetBinContent(m0,m12,1)/1.645;
      Double_t Ms2 = diff_effi_wminus_NNPDF->GetBinContent(m0,m12,1);
      Double_t Ms3 = diff_effi_wminus_MSTW->GetBinContent(m0,m12,1);

      

      central_value = 0.5*(TMath::Max(TMath::Max(x1+Ps1*x1,x2+Ps2*x2),x3+Ps3*x3) + TMath::Min(TMath::Min(x1-Ms1*x1,x2-Ms2*x2),x3-Ms3*x3));
      error = 0.5*(TMath::Max(TMath::Max(x1+Ps1*x1,x2+Ps2*x2),x3+Ps3*x3) - TMath::Min(TMath::Min(x1-Ms1*x1,x2-Ms2*x2),x3-Ms3*x3));

      //   cout << "m0 " << m0 << " M12 " << m12 << endl;
      if(central_value>0)std::cout << " central " << central_value << " error "<< error << " rel " << error/central_value << " m0 " << m0 << " m12 "<< m12 << std::endl;
      if(central_value > 0){
	final_pdf_mean->SetBinContent(m0,m12,1,central_value);
	final_pdf_error->SetBinContent(m0,m12,1,error/central_value);

	final_pdf_error_2d->SetBinContent(m0,m12,error/central_value);
      }
    }
    

  }

  output->Write();
  output->Close();
  delete output; 






}


int newpdfUnc(TH3D& diff_effi_mean,TH3D& diff_effi_wplus, TH3D& diff_effi_wminus, int nsets,bool nnpdfFlag,TString pdfset ){


  gStyle->SetPalette(1);

   // Path to input files
  TString path = "../results/";

  char h_name_plus[50];
  
 

  TH3D* CTEQ6_350[101];
  TH3D* CTEQ6_before[101];

 



  TString name = "m0_m12_mChi_0";


  TString name_before = "pdf_unc_"+pdfset+"_before";
  TString name_after = "pdf_unc_"+pdfset+"_350";

  for(int n = 0; n < nsets;n++){
    sprintf(h_name_plus, "m0_m12_%d",n);
    std::cout << " i " << n << std::endl;

 
    CTEQ6_350[n] = getHisto("../results/",h_name_plus,"AK5Calo_mySUSYTopo1_all.root",name_after,1);
    CTEQ6_before[n] = getHisto("../results/",h_name_plus,"AK5Calo_mySUSYTopo1_all.root",name_before,1);
    
    CTEQ6_350[n]->Divide(CTEQ6_before[n]);
  }

  unsigned int npairs = (nsets-1)/2;
  
  for(int m0 = 0; m0 < CTEQ6_350[0]->GetNbinsX();m0++){
    
    for(int m12 = 0; m12 < CTEQ6_350[0]->GetNbinsY();m12++){

      double wplus = 0;
      double wminus = 0;

      unsigned int nplus = 0;
      unsigned int nminus = 0;
      
     
      for(unsigned int n = 0; n < npairs;n++){
	double wa = 0;
	double wb = 0;
	if(CTEQ6_350[0]->GetBinContent(m0,m12,1) > 0 && CTEQ6_350[2*n+1]->GetBinContent(m0,m12,1) != 0 && CTEQ6_350[2*n+2]->GetBinContent(m0,m12,1) != 0 ){
	  wa = CTEQ6_350[2*n+1]->GetBinContent(m0,m12,1)/CTEQ6_350[0]->GetBinContent(m0,m12,1)-1;
	  wb = CTEQ6_350[2*n+2]->GetBinContent(m0,m12,1)/CTEQ6_350[0]->GetBinContent(m0,m12,1)-1;
	}
	
	//	if(wa != 0 || wb != 0)std::cout << " wa " << wa << " wb " << wb << std::endl;

	if(nnpdfFlag){
	  //  cout << "here "<< endl;
	  if(wa > 0.){
	    wplus += wa*wa;
	    nplus++;
	  }else{

	    wminus +=wa*wa;
	    nminus++;
	  }
	  if(wb > 0.){
	    wplus += wb*wb;
	    nplus++;
	  }else{

	    wminus +=wb*wb;
	    nminus++;

	    // if(wminus > 0)std::cout << " wminus " << wminus << std::endl;
	  }
	}
	else{
	  if(wa > wb){
	    if(wa<0.) wa = 0;
	    if(wb>0.) wb = 0;
	    wplus += wa*wa;
	    wminus += wb*wb;
	  }else{
	    if(wb<0.) wb =0.;
	    if(wa>0.) wa = 0.;
	    wplus+=wb*wb;
	    wminus+=wa*wa;
	  }


	}//end else nnpdfflab

      }//end for loop 

      if(wplus > 0) wplus= sqrt(wplus);
      if(wminus > 0) wminus = sqrt(wminus);
      if(nnpdfFlag){
	if(nplus > 0) wplus /= sqrt(nplus);
	if(nminus > 0)wminus /= sqrt(nminus);
      }
      std::cout << pdfset << " default " << CTEQ6_350[0]->GetBinContent(m0,m12,1) << " wplus " << wplus << " wminus " << wminus << std::endl;

      diff_effi_wplus.SetBinContent(m0,m12,1,wplus);
      diff_effi_wminus.SetBinContent(m0,m12,1,wminus);
      diff_effi_mean.SetBinContent(m0,m12,1,CTEQ6_350[0]->GetBinContent(m0,m12,1));

    }

  }

  return 1;

}



TH3D* getHisto( TString path,
	       TString nameHist,
	       TString nameFile,
	       TString Dirname, 
	       int rebin ) {
  TString name = path + nameFile;
  TFile* file =  new TFile(name);
  TDirectory* dir = (TDirectory*)file->Get(Dirname);
  TH3D* hist = (TH3D*)dir->Get(nameHist);
  if (!hist) {
    std::cout << " name: " << nameHist
	      << " file: " << nameFile
	      << " dir: " <<  Dirname
	      << std::endl;
    abort();

  }
 
  return hist;
}
