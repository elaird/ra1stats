import ROOT as r

def sliceTH3(name, th3, axes = "yx",
             condition = "", inclusive = True) :
    ''' 1) Clone the th3.
        2) Zero the bins failing the conditions.
          * condition is evaluated at the corners of the bin.
          * 'inclusive' means all evaluations must pass condition.
        3) Return the requested projection. '''
    
    def evalCondition(x,y,z) : return eval(condition)
    
    def zeroBins(c) :
        axes = [c.GetXaxis(), c.GetYaxis(), c.GetZaxis()]
        for iBins in [(x+1,y+1,z+1) \
                         for x in range(c.GetNbinsX()) \
                         for y in range(c.GetNbinsY()) \
                         for z in range(c.GetNbinsZ())] :
            if 0 == c.GetBinContent(*iBins) == c.GetBinError(*iBins) : continue
            width = [(0,axis.GetBinWidth(bin)) for bin,axis in zip(iBins,axes)]
            low   =   [axis.GetBinLowEdge(bin) for bin,axis in zip(iBins,axes)]
            points = [(low[0]+wx,low[1]+wy,low[2]+wz) for wx in width[0] for wy in width[1] for wz in width[2]]
            passing = [evalCondition(*point) for point in points]
            if (inclusive and not any(passing) ) or ((not inclusive) and not all(passing)) :
                bin = c.GetBin(*iBins)
                c.SetBinContent(bin,0)
                c.SetBinError(bin,0)

    clone3 = th3.Clone(name)
    if condition : zeroBins(clone3)
    th2 = clone3.Project3D(axes); del clone3
    clone2 = th2.Clone(name);     del th2
    clone2.SetTitle(condition)
    return clone2
