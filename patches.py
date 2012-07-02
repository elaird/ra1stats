import collections

def cutFunc() :
    return {"T1":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
            "T2":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
            "T2tt":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
            "T2bb":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
            "T5zz":lambda iX,x,iY,y,iZ,z:(y<(x-200.1) and iZ==1 and x>399.9),
            "T1bbbb":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
            "T1tttt":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
            "T1tttt_2012":lambda iX,x,iY,y,iZ,z:(y<(x-150.1) and iZ==1 and x>299.9),
            }

def nEventsIn() :
    return {""       :(1,     None),
            "T5zz"   :(5.0e3, None),
            }

def overwriteInput() :
    return collections.defaultdict(list)

def overwriteOutput() :
    out = collections.defaultdict(list)
    out.update({"T2": [(9,2,1)],
                "T2bb": [
                (16, 9, 1), (18, 2, 1), (20, 3, 1), (20, 14, 1), (21, 1, 1),
                (22, 5, 1), (22, 15, 1), (23, 12, 1), (25, 17, 1), (26, 14, 1),
                (27, 13, 1), (28, 13, 1), (28, 19, 1), (29, 7, 1), (29, 9, 1),
                (29, 18, 1), (30, 4, 1), (31, 4, 1), (31, 6, 1), (31, 20, 1),
                (31, 23, 1), (33, 4, 1), (33, 5, 1), (33, 16, 1), (33, 20, 1),
                (33, 21, 1), (33, 22, 1), (33, 25, 1), (33, 26, 1), (35, 17, 1),
                (36, 13, 1), (36, 26, 1), (39, 9, 1), (39, 32, 1), (40, 5, 1),
                (40, 34, 1), (41, 11, 1), (41, 16, 1), (41, 20, 1), (41, 23, 1),
                (41, 27, 1), (42, 21, 1), (42, 29, 1), (42, 31, 1), (42, 33, 1),
                (43, 13, 1), (44, 6, 1), (44, 9, 1), (44, 17, 1), (44, 26, 1),
                (44, 31, 1), (44, 33, 1), (20, 12, 1), (31,2,1)
                ],
                "T1bbbb": [ (36, 29, 1) ],
                "T1tttt": [
                (37, 2, 1), (37, 3, 1), (37, 4, 1), (37, 5, 1), (37, 6, 1),
                (37, 7, 1), (29, 13, 1), (40, 24, 1), (44, 28, 1),
                (27, 11, 1)
                ],
                })
    return out

def graphBlackLists() :
    out = {}
    keys  = [ "UpperLimit", "ExpectedUpperLimit" ]
    keys += [ "ExpectedUpperLimit_%+d_Sigma" % i for i in [-1,1] ]
    keys += [ "UpperLimit_%+d_Sigma" % i for i in [-1,1] ]
    for key in keys :
        out[key] = collections.defaultdict(list)

    out["UpperLimit"].update({"T1" : [ (1000,125), (1000,175) ]})
    out["UpperLimit_-1_Sigma"].update({"T1":[ (950, 350) ]})
    out["UpperLimit_+1_Sigma"].update({"T1":[ (1050,50), (1025, 375),
        (1025, 400), (1000,425) ]})

    out["UpperLimit"].update({"T2" : [ (800,200) ]})
    out["UpperLimit_-1_Sigma"].update({"T2":[ (750, 200), (675,300),
        (525,300) ]})
    out["UpperLimit_+1_Sigma"].update({"T2":[ (575,400), (725,325), (700,300),
        (750,250), (775,200), (825,275), (800,250), (850,225), (850,75),
        (875,75), (725,250)]})
    out["ExpectedUpperLimit_-1_Sigma"].update({"T2" : [ (875,150) ]})

    out["UpperLimit"].update({"T2bb" : [ (500,100), (500,250),
        (575,125), (500, 150), (525,200), (500,200) ]})

    out["UpperLimit_-1_Sigma"].update({"T2bb" : [ (525,150), (475, 200)]})
    out["UpperLimit_+1_Sigma"].update({"T2bb" : [ (575,125), (500, 250), (550, 200), (575, 200), (500,150), (525,200)]})

    out["ExpectedUpperLimit_-1_Sigma"].update({"T2bb" : [ (500,250),
        (525,225), (525,100), (525,200)]})
    out["ExpectedUpperLimit_+1_Sigma"].update({"T2bb" : [ (475, 75), ]})

    out["UpperLimit"].update({"T2tt" : [ (550,100), (525,150), (450,50), (475,100) ]})
    out["UpperLimit_-1_Sigma"].update({"T2tt":[ (550, 100) ]})
    out["UpperLimit_+1_Sigma"].update({"T2tt":[ (550, 100), (575,125),
        (525,150), (475,125) ]})
    out["ExpectedUpperLimit_-1_Sigma"].update({"T2tt" : [ (450,50), (375,50)]})

    out["UpperLimit"].update({"T1bbbb" : [ (1050,200), (1050,250),
        (1075,650), (1050,400), (1025,475), (975,650), (1050,450), (950,625),
        (975,550), (1000,525), (1025,525), (1050,475), (1000,575), (1000,625),
        (1025,625), (1050,600)]})
    out["ExpectedUpperLimit_-1_Sigma"].update({"T1bbbb" :
        [(1050,75), (1100,200), (975,625), (875, 625), (925,575), (900,575),
        (875,575), (850,575), (825,575), (1025,575), (1050,450) ]})
    out["ExpectedUpperLimit"].update({"T1bbbb" : [ (1025,475),
        (1025,450) ]})

    out["UpperLimit"].update({"T1tttt" : [ (550,150), (800,350),
        (750,300), (800,300), (800,250), (825,200), (825,250), (875,300) ]})
    out["UpperLimit_-1_Sigma"].update({"T1tttt" : [ (550,150), (600,100),
        (600,150), (725,200), (750,200), (875,175) ]})
    out["UpperLimit_+1_Sigma"].update({"T1tttt" : [ (550,150), (825,200),
        (825,250), (875,350), (900,350), (925,300), (900,300)]})

    out["ExpectedUpperLimit"].update({"T1tttt" : [(825,175)] })
    out["ExpectedUpperLimit_+1_Sigma"].update({"T1tttt" :
        [(675,175), (750, 125) ]})
    out["ExpectedUpperLimit_-1_Sigma"].update({"T1tttt" :
        [(875,350), (900,150), (900,200), (1000,225), (925,225), (950,275),
        (950,300), (900,325), (850,325)]})

    return out
