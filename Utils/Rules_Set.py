def get_default():
    raise ValueError("action error")

def rule0():
    pass

def rule1():
    pass

def rule2():
    pass

def rule3():
    pass

def rule4():
    pass

def rule5():
    pass

def rule6():
    pass

def rule7():
    pass

def rule8():
    pass

def rule9():
    pass

def rule10():
    pass

def pick_rules(case):
    switcher = {
        0: rule0,
        1: rule1,
        2: rule2,
        3: rule3,
        4: rule4,
        5: rule5,
        6: rule6,
        7: rule7,
        8: rule8,
        9: rule9,
        10: rule10,
    }
    return switcher.get(case, get_default)()

