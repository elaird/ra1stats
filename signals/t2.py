import common
from configuration.signal import processStamp, pruned

t2 = common.signal(xs = 0.8*0.244862, effUncRel = 0.134,
                   label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2")["text"]),
                                                               "0.8 (m_{#tilde{q}}= 600 GeV, m_{#tilde{#chi}^{0}_{1}} = 250 GeV)"))
t2.insert("0b_le3j", {"effHad":[0.012000, 0.017700, 0.054700, 0.048300, 0.022800, 0.010100, 0.002700, 0.002400],})

t2_0 = common.signal(xs = 0.244862, effUncRel = 0.134,
                   label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2")["text"]),
                                                               "1.0 (m_{#tilde{q}}= 600 GeV, m_{#tilde{#chi}^{0}_{1}} = 250 GeV)"))
t2_0.insert("0b_le3j", {"effHad":[0.012000, 0.017700, 0.054700, 0.048300, 0.022800, 0.010100, 0.002700, 0.002400],})

t2_1 = common.signal(xs = 0.8*0.0473374, effUncRel = 0.134,
                     label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2")["text"]),
                                                               "0.8 (m_{#tilde{q}}= 750 GeV, m_{#tilde{#chi}^{0}_{1}} = 0 GeV)"))
t2_1.insert("0b_le3j", {"effHad":[0.002000, 0.003600, 0.015502, 0.033103, 0.041304, 0.041904, 0.033003, 0.030803]})

t2_2 = common.signal(xs = 0.1*1.67947, effUncRel = 0.134,
                      label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2")["text"]),
                                                               "0.1 (m_{#tilde{q}}= 450 GeV, m_{#tilde{#chi}^{0}_{1}} = 0 GeV)"))
t2_2.insert("0b_le3j", {"effHad":[0.019808, 0.027411, 0.060624, 0.044518, 0.015206, 0.004202, 0.000900, 0.000800]})

t2_3 = common.signal(xs = 0.1*7.98294, effUncRel = 0.134,
                      label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2")["text"]),
                                                               "0.1 (m_{#tilde{q}}= 350 GeV, m_{#tilde{#chi}^{0}_{1}} = 100 GeV)"))
t2_3.insert("0b_le3j", {"effHad":[0.037207, 0.032807, 0.027005, 0.009302, 0.002300, 0.000500, 0.000100, 0.000000]})
