def benchmarkPoints() :
    out = {}
    fields =                       [  "m0",  "m12",  "A0", "tanBeta", "sgn(mu)"]
    #out["LM0" ] = dict(zip(fields, [   200,    160,  -400,        10,         1]))
    #out["LM1" ] = dict(zip(fields, [    60,    250,     0,        10,         1]))
    out["LM2" ] = dict(zip(fields, [   185,    350,     0,        35,         1]))
    out["LM3" ] = dict(zip(fields, [   330,    240,     0,        20,         1]))
    #out["LM4" ] = dict(zip(fields, [   210,    285,     0,        10,         1]))
    #out["LM5" ] = dict(zip(fields, [   230,    360,     0,        10,         1]))
    #out["LM6" ] = dict(zip(fields, [    85,    400,     0,        10,         1]))
    out["LM7" ] = dict(zip(fields, [  3000,    230,     0,        10,         1]))
    out["LM8" ] = dict(zip(fields, [   500,    300,  -300,        10,         1]))
    out["LM9" ] = dict(zip(fields, [  1450,    175,     0,        50,         1]))
    out["LM10"] = dict(zip(fields, [  3000,    500,     0,        10,         1]))
    out["LM11"] = dict(zip(fields, [   250,    325,     0,        35,         1]))
    out["LM12"] = dict(zip(fields, [  2545,    247,  -866,        48,         1]))
    out["LM13"] = dict(zip(fields, [   270,    218,  -553,        40,         1]))

    #out["IM1" ] = dict(zip(fields, [   100,    510,     0,        10,         1]))
    #out["IM2" ] = dict(zip(fields, [   180,    510,     0,        10,         1]))
    #out["IM3" ] = dict(zip(fields, [   260,    450,     0,        10,         1]))
    out["IM4" ] = dict(zip(fields, [   820,    390,     0,        10,         1]))

    out["RM1" ] = dict(zip(fields, [   320,    520,     0,        10,         1]))
    out["RM2" ] = dict(zip(fields, [  1800,    280,     0,        10,         1]))
    return out

def scanParameters() :
    out = {}
    fields =                            ["A0", "tanBeta", "sgn(mu)"]
    out["tanBeta3" ] = dict(zip(fields, [   0,         3,         1]))
    out["tanBeta10"] = dict(zip(fields, [   0,        10,         1]))
    out["tanBeta50"] = dict(zip(fields, [   0,        50,         1]))
    return out

def processes() :
    return ["gg", "sb", "ss", "sg", "ll", "nn", "ng", "bb", "tb", "ns"]

def processStamp(key = "") :
    chi = "#tilde{#chi}^{0}_{1}"
    dct = {
        ''     : {
        'text': "",
        'xpos': 0.4250,
        },
        'T2'     : {
        'text': "pp #rightarrow #tilde{q} #tilde{q}, #tilde{q} #rightarrow q %s; m(#tilde{g})>>m(#tilde{q})"%chi,
        'xpos': 0.4250,
        },
        'T2bb'   : {
        'text': "pp #rightarrow #tilde{b} #tilde{b}, #tilde{b} #rightarrow b %s; m(#tilde{g})>>m(#tilde{b})"%chi,
        'xpos': 0.425,
        },
        'T2tt'   : {
        'text': "pp #rightarrow #tilde{t} #tilde{t}, #tilde{t} #rightarrow t %s; m(#tilde{g})>>m(#tilde{t})"%chi,
        'xpos': 0.41,
        },
        'T1'     : {
        'text': "pp #rightarrow #tilde{g} #tilde{g}, #tilde{g} #rightarrow q #bar{q} %s; m(#tilde{q})>>m(#tilde{g})"%chi,
        'xpos': 0.4325,
        },
        'T1bbbb' : {
        'text': "pp #rightarrow #tilde{g} #tilde{g}, #tilde{g} #rightarrow b #bar{b} %s; m(#tilde{b})>>m(#tilde{g})"%chi,
        'xpos': 0.43,
        },
        'T1tttt' : {
        'text': "pp #rightarrow #tilde{g} #tilde{g}, #tilde{g} #rightarrow t #bar{t} %s; m(#tilde{t})>>m(#tilde{g})"%chi,
        'xpos': 0.425,
        },
        }
    return dct.get(key, dct[""])
