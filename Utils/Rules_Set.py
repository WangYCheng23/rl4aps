def get_default():
    raise ValueError("action error")

def rule0(situation):
    ## 选取离交付最远的未超时工件  或者  预估超时最大的工件，
    ## 选择工件最小的完成时间点的机器和模具
    # 1.choose job
    # 2.choose machine
    pass

def rule1(situation):
    ## 选取 剩余时间/执行时间 最小(预估空余时间最少)的未超时工件  或者  预估超时最大的工件，
    ## 选择工件最小的完成时间点的机器和模具
    # 1.choose job
    # 2.choose machine   
    pass

def rule2(situation):
    ## 选取预估超时最长的未完成工件， 一半概率选择利用率最小的机器，一半概率选择执行工作总时间最小的机器
    # 1.choose job
    # 2.choose machine  
    pass

def rule3(situation):
    ## 随机选择一个未完成的工件， 取最短执行时间点的候选机器    
    pass

def rule4(situation):
    ##选取当前时间距离交付最近或者可能延期最长的job， 取最短执行时间点的候选机器
    pass

def rule5(situation):
    ##选取可能延期最长的job， 取最短执行时间点的候选机器
    pass

def rule6(situation):
    ##选取可能延期最长的job
    pass

def rule7(situation):
    ##选取可能延期最长的job
    pass

def rule8(situation):
     ##选取可能延期最长的job
    pass

def rule9(situation):
    pass

def rule10(situation):
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

