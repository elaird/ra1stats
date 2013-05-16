import common
from configuration.signal import processStamp, pruned

a = common.signal(xs = 0.8*0.244862, effUncRel = 0.134,
                   label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2")["text"]),
                                                               "0.8 (m_{#tilde{q}}= 600 GeV, m_{#tilde{#chi}^{0}_{1}} = 250 GeV)"))
a.insert("0b_le3j", {"effHad":[0.012000, 0.017700, 0.054700, 0.048300, 0.022800, 0.010100, 0.002700, 0.002400],})


a_0 = common.signal(xs = 0.244862, effUncRel = 0.134,
                   label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2")["text"]),
                                                               "1.0 (m_{#tilde{q}}= 600 GeV, m_{#tilde{#chi}^{0}_{1}} = 250 GeV)"))
a_0.insert("0b_le3j", {"effHad":[0.012000, 0.017700, 0.054700, 0.048300, 0.022800, 0.010100, 0.002700, 0.002400],})


b = common.signal(xs = 0.8*0.0473374, effUncRel = 0.134,
                     label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2")["text"]),
                                                               "0.8 (m_{#tilde{q}}= 750 GeV, m_{#tilde{#chi}^{0}_{1}} = 0 GeV)"))
b.insert("0b_le3j", {"effHad":[0.002000, 0.003600, 0.015502, 0.033103, 0.041304, 0.041904, 0.033003, 0.030803]})


c = common.signal(xs = 0.1*1.67947, effUncRel = 0.134,
                      label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2")["text"]),
                                                               "0.1 (m_{#tilde{q}}= 450 GeV, m_{#tilde{#chi}^{0}_{1}} = 0 GeV)"))
c.insert("0b_le3j", {"effHad":[0.019808, 0.027411, 0.060624, 0.044518, 0.015206, 0.004202, 0.000900, 0.000800]})


d = common.signal(xs = 0.1*7.98294, effUncRel = 0.134,
                      label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2")["text"]),
                                                               "0.1 (m_{#tilde{q}}= 350 GeV, m_{#tilde{#chi}^{0}_{1}} = 100 GeV)"))
d.insert("0b_le3j", {"effHad":[0.037207, 0.032807, 0.027005, 0.009302, 0.002300, 0.000500, 0.000100, 0.000000]})


e = common.signal(xs = 0.1*3.54338, effUncRel = 0.134,
                      label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2")["text"]),
                                                               "0.1 (m_{#tilde{q}}= 400 GeV, m_{#tilde{#chi}^{0}_{1}} = 25 GeV)"))

e.insert("0b_le3j", {"effHad":[0.025403, 0.030803, 0.060206, 0.022502, 0.006001, 0.002000, 0.000600, 0.000200]})



f = common.signal(xs = 0.1*3.54338, effUncRel = 0.134,
                      label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2")["text"]),
                                                               "0.1 (m_{#tilde{q}}= 400 GeV, m_{#tilde{#chi}^{0}_{1}} = 50 GeV)"))

f.insert("0b_le3j", {"effHad":[0.027305, 0.032206, 0.053411, 0.024905, 0.006801, 0.001700, 0.000500, 0.000200]})

g = common.signal(xs = 0.1*5.26422, effUncRel = 0.134,
                      label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2")["text"]),
                                                               "0.1 (m_{#tilde{q}}= 375 GeV, m_{#tilde{#chi}^{0}_{1}} = 50 GeV)"))

g.insert("0b_le3j", {"effHad":[0.029803, 0.038604, 0.050505, 0.016002, 0.003200, 0.001300, 0.000000, 0.000500]})
