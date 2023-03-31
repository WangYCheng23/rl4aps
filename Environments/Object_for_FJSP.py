import random

class Object_job:
    def __init__(self,I,job_color):
        self.I=I  ## id
        self.job_colour = job_color
        self.Start= None
        self.End= None
        self.T= None
        self.mould_assign_for=None
        self.machine_assign_for=None

    def _assign(self,S,E,mould,machine,t):
        ## S 开始时间
        ## E 结束时间
        ## mould:被安排的mould的id
        ## machine:被安排的machine的id
        ## t: 工序的pass-time
        self.Start =S
        self.End = E
        self.T = t
        self.mould_assign_for = mould
        self.machine_assign_for = machine

class Object_machine:
    def __init__(self,I,init_mould,init_colour):
        self.I=I  ## id
        self.init_mould = init_mould
        self.curr_mould = init_mould
        self.init_colour = init_colour
        self.Start=[]
        self.End=[]
        self.T=[]
        self.job_assign_for = []
        self.mould_assign_for = []

        self.Change_mould = []
        self.Change_colour = []

    def _add_job(self,S,E,job,mould,t):
        ## S 开始时间
        ## E 结束时间
        ## job:被安排的job的id
        ## mould:被安排的mould
        ## t: 工序的pass-time
        self.Start.append(S)
        self.End.append(E)
        self.Start.sort()
        self.End.sort()
        self.job_assign_for.insert(self.End.index(E),job)
        self.mould_assign_for.insert(self.End.index(E),mould)
        self.curr_mould = mould
        self.T.append(t) ### 不是执行顺序的 pass time

    def idle_time(self):
        Idle=[]
        if len(self.Start) > 0:
            if self.Start[0]!=0:
                Idle.append([0,self.Start[0]])
            for i in range(1,len(self.Start)):
                if self.Start[i]-self.End[i-1]>0:
                    K = [ self.End[i-1], self.Start[i] ]
                    Idle.append(K)
        return  Idle


class Object_mould:
    def __init__(self,I,init_machine):
        self.I=I  ## id
        self.init_machine = init_machine
        self.curr_machine = init_machine
        self.Start=[]
        self.End=[]
        self.T=[]
        self.job_assign_for = []
        self.machine_assign_for = []

        self.Change_mould = []
        self.Change_colour = []

    def _add_job(self,S,E,job,machine,t):
        ## S 开始时间
        ## E 结束时间
        ## job:被安排的job
        ## machine:被安排的machine
        ## t: 工序的pass-time
        self.Start.append(S)
        self.End.append(E)
        self.Start.sort()
        self.End.sort()
        self.job_assign_for.insert(self.End.index(E),job)
        self.machine_assign_for.insert(self.End.index(E),machine)
        self.curr_machine = machine
        self.T.append(t) ### 不是执行顺序的 pass time

    def idle_time(self):
        Idle=[]
        if len(self.Start) > 0:
            if self.Start[0]!=0:
                Idle.append([0,self.Start[0]])
            for i in range(1,len(self.Start)):
                if self.Start[i]-self.End[i-1]>0:
                    K = [self.End[i-1],self.Start[i]]
                    Idle.append(K)
        return  Idle
