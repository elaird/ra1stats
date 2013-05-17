import math
import common
from configuration.signal import pruned, processStamp

t1 = common.signal(xs = 0.433971, effUncRel = 0.140,
                   label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T1")["text"]),
                                                               "(m_{#tilde{g}}= 700 GeV, m_{#tilde{#chi}^{0}_{1}} = 300 GeV)"))
t1.insert("0b_ge4j", {"effHad":[0.000100, 0.000600, 0.007301, 0.022402, 0.030103, 0.017402, 0.010501, 0.009401],})


t2bb = common.signal(xs = 0.0855847, effUncRel = 0.131,
                     label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2bb")["text"]),
                                                                 "(m_{#tilde{b}}= 500 GeV, m_{#tilde{#chi}^{0}_{1}} = 150 GeV)"))
t2bb.insert("2b_le3j",{"effHad":[0.011400, 0.015000, 0.029300, 0.015000, 0.005800, 0.002000, 0.000500, 0.000300],})
t2bb.insert("1b_le3j",{"effHad":[0.013300, 0.013400, 0.026800, 0.015200, 0.005500, 0.001100, 0.000400, 0.000600],})

t2tt = common.signal(xs = 0.35683, effUncRel = 0.139,
                     label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2tt")["text"]),
                                                                 "(m_{#tilde{t}}= 400 GeV, m_{#tilde{#chi}^{0}_{1}} = 0 GeV)"))
t2tt.insert("1b_ge4j", {"effHad" :[0.001760, 0.002820, 0.006600, 0.005960, 0.003020, 0.001300, 0.000400, 0.000300],
                        #"effMuon":[0.000100, 0.000260, 0.000460, 0.000620, 0.000400, 0.000120, 0.000060, 0.000020],
                        })
t2tt.insert("2b_ge4j", {"effHad" :[0.001040, 0.001500, 0.004620, 0.004020, 0.002000, 0.000640, 0.000300, 0.000200],
                        #"effMuon":[0.000080, 0.000120, 0.000340, 0.000360, 0.000280, 0.000140, 0.000000, 0.000020],
                        })

t1tttt = common.signal(xs = 0.0966803, effUncRel = 0.230,
                       label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T1tttt")["text"]),
                                                                   "(m_{#tilde{g}}= 850 GeV, m_{#tilde{#chi}^{0}_{1}} = 250 GeV)"))
t1tttt.insert("ge4b_ge4j", {"effHad" :[0.000000, 0.000000, 0.003809],
                            #"effMuon":[0.000000, 0.000000, 0.000680],
                            })

t1bbbb = common.signal(xs = 0.060276, effUncRel = 0.160,
                       label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T1bbbb")["text"]),
                                                                   "(m_{#tilde{g}}= 900 GeV, m_{#tilde{#chi}^{0}_{1}} = 500 GeV)"))
t1bbbb.insert("3b_ge4j",{"effHad" :[0.000200, 0.000700, 0.003900, 0.009100, 0.012600, 0.006100, 0.004900, 0.003300],
                         #"effMuon":[0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000]
                         })


t2cc0 = common.signal(xs=36.8, effUncRel=0.20,
                     label="#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2cc")["text"]),
                                                               "(m_{#tilde{t}}= 175 GeV, m_{#tilde{#chi}^{0}_{1}} = 95 GeV)"))
t2cc0.insert("0b_ge4j", {"effHad":[0.000130, 0.000104, 0.000111, 0.000058, 0.000027, 0.000013, 0.000005, 0.000004]})
t2cc0.insert("0b_le3j", {"effHad":[0.000915, 0.000429, 0.000272, 0.000065, 0.000011, 0.000004, 0.000001, 0.000000]})
t2cc0.insert("1b_ge4j", {"effHad":[0.000065, 0.000049, 0.000060, 0.000042, 0.000022, 0.000006, 0.000005, 0.000000]})
t2cc0.insert("1b_le3j", {"effHad":[0.000326, 0.000126, 0.000084, 0.000014, 0.000003, 0.000000, 0.000000, 0.000000]})
t2cc0.insert("2b_ge4j", {"effHad":[0.000015, 0.000013, 0.000014, 0.000008, 0.000004, 0.000001, 0.000000, 0.000001]})
t2cc0.insert("2b_le3j", {"effHad":[0.000032, 0.000011, 0.000003, 0.000001, 0.000001, 0.000000, 0.000000, 0.000000]})


t2cc02 = common.signal(xs=36.8, effUncRel=0.20,
                      label="#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2cc")["text"]),
                                                                "(m_{#tilde{t}}= 175 GeV, m_{#tilde{#chi}^{0}_{1}} = 165 GeV)"))
t2cc02.insert("0b_ge4j", {"effHad":[0.000054, 0.000054, 0.000100, 0.000060, 0.000044, 0.000016, 0.000006, 0.000006]})
t2cc02.insert("0b_le3j", {"effHad":[0.001245, 0.000592, 0.000452, 0.000159, 0.000035, 0.000015, 0.000006, 0.000001]})
t2cc02.insert("1b_ge4j", {"effHad":[0.000004, 0.000003, 0.000008, 0.000012, 0.000010, 0.000001, 0.000000, 0.000002]})
t2cc02.insert("1b_le3j", {"effHad":[0.000076, 0.000028, 0.000031, 0.000011, 0.000004, 0.000002, 0.000001, 0.000000]})
t2cc02.insert("2b_ge4j", {"effHad":[0.000003, 0.000001, 0.000002, 0.000001, 0.000000, 0.000000, 0.000000, 0.000000]})
t2cc02.insert("2b_le3j", {"effHad":[0.000013, 0.000001, 0.000004, 0.000000, 0.000001, 0.000000, 0.000000, 0.000000]})

t2cc = common.signal(xs=36.8, effUncRel=0.20,
                     label="#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2cc")["text"]),
                                                               "(m_{#tilde{t}}= 175 GeV, m_{#tilde{#chi}^{0}_{1}} = 95 GeV)"))
t2cc.insert("0b_ge4j", {"effHad":[0.000142, 0.000114, 0.000140, 0.000103, 0.000050, 0.000029, 0.000017, 0.000017]})
t2cc.insert("0b_le3j", {"effHad":[0.001117, 0.000544, 0.000401, 0.000108, 0.000026, 0.000012, 0.000006, 0.000003]})
t2cc.insert("1b_ge4j", {"effHad":[0.000095, 0.000072, 0.000092, 0.000085, 0.000041, 0.000027, 0.000022, 0.000004]})
t2cc.insert("1b_le3j", {"effHad":[0.000525, 0.000255, 0.000171, 0.000044, 0.000018, 0.000008, 0.000000, 0.000004]})

t2cc2 = common.signal(xs=36.8, effUncRel=0.20,
                      label="#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2cc")["text"]),
                                                                "(m_{#tilde{t}}= 175 GeV, m_{#tilde{#chi}^{0}_{1}} = 165 GeV)"))
t2cc2.insert("0b_ge4j", {"effHad":[0.000058, 0.000057, 0.000118, 0.000086, 0.000065, 0.000038, 0.000020, 0.000014]})
t2cc2.insert("0b_le3j", {"effHad":[0.001495, 0.000799, 0.000729, 0.000298, 0.000086, 0.000036, 0.000026, 0.000013]})
t2cc2.insert("1b_ge4j", {"effHad":[0.000007, 0.000005, 0.000031, 0.000029, 0.000022, 0.000007, 0.000001, 0.000007]})
t2cc2.insert("1b_le3j", {"effHad":[0.000203, 0.000082, 0.000113, 0.000048, 0.000020, 0.000006, 0.000007, 0.000004]})


def effQcdLike(k=None, eff0=None, iBin=None):
    # take14a
    htMeans = (298.0, 348.0, 416.0, 517.0, 617.0, 719.0, 819.0, 1044.)
    bulk = (559500000, 252400000, 180600000, 51650000,  # le3j
            17060000, 6499000, 2674000, 2501000)
    f = math.exp(-k*(htMeans[iBin]-htMeans[0]))*bulk[i]/(0.0+bulk[0])
    return eff0*f

t2ccQcdLike = common.signal(xs=36.8, effUncRel=0.20, label="SM + QCD-like (k=0.03)")
t2ccQcdLike.insert("0b_le3j", {"effHad":[effQcdLike(k=0.03, eff0=0.005, iBin=i) for i in range(8)]})

