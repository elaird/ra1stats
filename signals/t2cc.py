import math
import common
from configuration.signal import pruned, processStamp
from configuration.units import pb

def effQcdLike(k=None, eff0=None, iBin=None):
    # take14a
    htMeans = (298.0, 348.0, 416.0, 517.0, 617.0, 719.0, 819.0, 1044.)
    bulk = (559500000, 252400000, 180600000, 51650000,  # le3j
            17060000, 6499000, 2674000, 2501000)
    f = math.exp(-k*(htMeans[iBin]-htMeans[0]))*bulk[i]/(0.0+bulk[0])
    return eff0*f

qcdLike = common.signal(xs=36.8, effUncRel=0.20, label="SM + QCD-like (k=0.03)")
qcdLike.insert("0b_le3j", {"effHad":[effQcdLike(k=0.03, eff0=0.005, iBin=i) for i in range(8)]})

far8 = common.signal(xs=36.8*pb, effUncRel=0.20,
                     label="#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2cc")["text"]),
                                                               "(m_{#tilde{t}}= 175 GeV, m_{#tilde{#chi}^{0}_{1}} = 95 GeV)"))
far8.insert("0b_ge4j", {"effHad":[0.000142, 0.000114, 0.000140, 0.000103, 0.000050, 0.000029, 0.000017, 0.000017]})
far8.insert("0b_le3j", {"effHad":[0.001117, 0.000544, 0.000401, 0.000108, 0.000026, 0.000012, 0.000006, 0.000003]})
far8.insert("1b_ge4j", {"effHad":[0.000095, 0.000072, 0.000092, 0.000085, 0.000041, 0.000027, 0.000022, 0.000004]})
far8.insert("1b_le3j", {"effHad":[0.000525, 0.000255, 0.000171, 0.000044, 0.000018, 0.000008, 0.000000, 0.000004]})

near8 = common.signal(xs=36.8*pb, effUncRel=0.20,
                      label="#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2cc")["text"]),
                                                                "(m_{#tilde{t}}= 175 GeV, m_{#tilde{#chi}^{0}_{1}} = 165 GeV)"))
near8.insert("0b_ge4j", {"effHad":[0.000058, 0.000057, 0.000118, 0.000086, 0.000065, 0.000038, 0.000020, 0.000014]})
near8.insert("0b_le3j", {"effHad":[0.001495, 0.000799, 0.000729, 0.000298, 0.000086, 0.000036, 0.000026, 0.000013]})
near8.insert("1b_ge4j", {"effHad":[0.000007, 0.000005, 0.000031, 0.000029, 0.000022, 0.000007, 0.000001, 0.000007]})
near8.insert("1b_le3j", {"effHad":[0.000203, 0.000082, 0.000113, 0.000048, 0.000020, 0.000006, 0.000007, 0.000004]})

near10 = common.signal(xs=36.8*pb, effUncRel=0.20,
                      label="#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2cc")["text"]),
                                                                "(m_{#tilde{t}}= 175 GeV, m_{#tilde{#chi}^{0}_{1}} = 165 GeV)"))
near10.insert("0b_ge4j", {"effHad":[0.000003, 0.000063, 0.000062, 0.000130, 0.000096, 0.000075, 0.000044, 0.000023, 0.000009, 0.000008]})
near10.insert("0b_le3j", {"effHad":[0.002931, 0.001586, 0.000853, 0.000789, 0.000331, 0.000099, 0.000043, 0.000031, 0.000006, 0.000011]})
near10.insert("1b_ge4j", {"effHad":[0.000000, 0.000005, 0.000004, 0.000019, 0.000018, 0.000015, 0.000004, 0.000001, 0.000002, 0.000004]})
near10.insert("1b_le3j", {"effHad":[0.000182, 0.000128, 0.000046, 0.000067, 0.000030, 0.000010, 0.000003, 0.000003, 0.000002, 0.000000]})

far10 = common.signal(xs=36.8*pb, effUncRel=0.20,
                     label="#lower[0.25]{#splitline{%s}{%s}}"%("SM + "+pruned(processStamp("T2cc")["text"]),
                                                               "(m_{#tilde{t}}= 175 GeV, m_{#tilde{#chi}^{0}_{1}} = 95 GeV)"))
far10.insert("0b_ge4j", {"effHad":[0.000002, 0.000163, 0.000131, 0.000163, 0.000121, 0.000059, 0.000036, 0.000021, 0.000015, 0.000008]})
far10.insert("0b_le3j", {"effHad":[0.002167, 0.001254, 0.000613, 0.000456, 0.000125, 0.000031, 0.000015, 0.000008, 0.000000, 0.000004]})
far10.insert("1b_ge4j", {"effHad":[0.000000, 0.000079, 0.000056, 0.000077, 0.000070, 0.000032, 0.000022, 0.000013, 0.000003, 0.000000]})
far10.insert("1b_le3j", {"effHad":[0.000626, 0.000418, 0.000195, 0.000129, 0.000031, 0.000014, 0.000004, 0.000000, 0.000001, 0.000001]})
