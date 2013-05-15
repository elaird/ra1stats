def ExpectedUpperLimit_m1_Sigma():
    return {"blackList": [],
            "replace": {},
            }


def ExpectedUpperLimit_p1_Sigma():
    return {"blackList": [],
            "replace": {},
            }


def ExpectedUpperLimit():
    return {"blackList": [],
            "replace": {},
            }


def UpperLimit():
    return {"blackList": [(450,275),(475,250),(525,275),(575,300),(625,325),(650,325)],
            "replace": {(425,250):(430,250),(500,275):(500,285),(550,300):(550,310),
                        (675,325):(670,320.0),(775,150):(770,150)}
            }


def UpperLimit_p1_Sigma():
    return {"blackList": [],
            "replace": {},
            }


def UpperLimit_m1_Sigma():
    return {"blackList": [(450,275),(475,250),(500,250),(550,300),(575,275),(600,300),(675,300)], #(525,275),
            "replace": {(425,250):(430,250),(525,275):(525,282.5),(750,75):(745,75)},
            }
