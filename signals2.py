from signals import common,pruned,processStamp

t1 = common.signal(xs = 0.433971, effUncRel = 0.140,
                   label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T1")["text"]),
                                                               "(m_{#tilde{g}}= 700 GeV, m_{#tilde{#chi}^{0}_{1}} = 300 GeV)"))
t1.insert("0b_ge4j", {"effHad":[0.000100, 0.000600, 0.007301, 0.022402, 0.030103, 0.017402, 0.010501, 0.009401],})

t2 = common.signal(xs = 0.244862, effUncRel = 0.134,
                   label = "#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2")["text"]),
                                                               "(m_{#tilde{q}}= 600 GeV, m_{#tilde{#chi}^{0}_{1}} = 250 GeV)"))
t2.insert("0b_le3j",{"effHad":[0.012000, 0.017700, 0.054700, 0.048300, 0.022800, 0.010100, 0.002700, 0.002400],})

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
                         "effMuon":[0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.000000]})
