import yaml
import time
import gymnasium
import numpy as np
from Object_for_FJSP import Object_job, Object_machine, Object_mould

class JSSPEnv(gymnasium.Env):
    def __init__(self, parameters):
        super().__init__()
        self.parameters = parameters
        self.observation_space = gymnasium.spaces.Box(shape=(1,10), dtype=np.float64)
        self.action_space = gymnasium.spaces.Box(shape=(1,3), dtype=np.int32)   # 订单，模具，机器

    def reset(self)->np.ndarray:
        """
        Reset Env
        """
        self.count_steps = 0
        self.construct_scene()
        obs = np.zeros(10).unsqueeze()
        self.old_obs = obs
        return obs  

    def step(self, action: np.ndarray):
        """
        Step Env
        """
        self.count_steps += 1
        self.schedule(action)
        obs = self.extract_features()
        reward_info, reward = self.cal_reward(self.old_obs, obs.unsequeeze())
        self.old_obs = obs
        terminal = True if self.count_steps==self.jobs_num-1 else False
        return obs, reward, terminal, reward_info

    def cal_reward(self, old_obs, next_obs):
        """
        :param Std_C_J_t: Tard_a(t)   t时刻的实际迟到率
        :param Mean_C_J_t: Tard_e(t)   t时刻的预估迟延率
        :param Std_C_J_t1: Tard_a(t+1)  t+1时刻的实际迟到率
        :param Mean_C_J_t1: Tard_e(t+1)  t+1时刻的预估迟延率
        :param Mean_U_t: U_ave(t)     t时刻的机器平均利用率
        :param Mean_U_t1: U_ave(t+1)  t+1时刻的机器平均利用率
        """
        Std_C_J_t, Mean_C_J_t, Mean_U_t, MhCH_t, MdCH_t = old_obs[0][5], old_obs[0][4], old_obs[0][0], old_obs[0][8], old_obs[0][9]
        Std_C_J_t1, Mean_C_J_t1, Mean_U_t1, MhCH_t1, MdCH_t1 = next_obs[0][5], next_obs[0][4], next_obs[0][0], next_obs[0][8], next_obs[0][9] 

        reward_prime = Std_C_J_t1*2 + MhCH_t1
        reward =   Std_C_J_t*2  + MhCH_t

        if reward_prime < reward:
            rt = 4
            tout = '延迟换模 奖励4'
        elif reward_prime > reward:
            rt = -4
            tout = '延迟换模 惩罚-4'
        else:
            if Mean_C_J_t1<Mean_C_J_t:
                rt = 1
                tout = '预估延迟率 奖励'
            else:
                if Mean_C_J_t1>Mean_C_J_t:
                    rt =-1
                    tout = '预估延迟率 惩罚'
                else:
                    if MdCH_t1 < MdCH_t:
                        rt = 1
                        tout = '模具换模率 奖励'
                    else:
                        if MdCH_t1 > MdCH_t:
                            rt = -1
                            tout = '模具换模率 惩罚'
                        else:
                            if Mean_U_t1>Mean_U_t:
                                rt=1
                                tout = '机器利用率 奖励'
                            else:
                                if Mean_U_t1>0.95*Mean_U_t:
                                    rt=0
                                    tout = '机器利用率 不变'
                                else:
                                    rt=-1
                                    tout = '机器利用率 惩罚'
        return tout, rt
    
    def extract_features(self):
        """
        Extract features for Agent to Observe
        """
        # To Do: Change to input -> Net -> output
        Avg_Utlization_Mh = np.mean(self.utilization_Mh)
        Std_Utlization_Mh = np.std(self.utilization_Mh)
        Avg_Utlization_Md = np.mean(self.utilization_Md)
        Std_Utlization_Md = np.std(self.utilization_Md)
        Avg_Complete_Jobs = np.mean(self.complete_procedures_J)
        Std_Complete_Jobs = np.std(self.complete_procedures_J)

        Avg_Complete_Machines = np.mean(self.compleMean_C_J_time_endMh)
        
        machine_change_rate = 0
        mould_change_rate = 0
        # 机器平均利用率, 机器的使用率标准差, 模具平均利用率, 模具的使用率标准差, 平均工件工序完成率, 工件工序完成率标准差
        # 未完成工件的预估迟延率, 实际的迟到率, 机器换模率, 模具换模率
        return Avg_Utlization_Mh, Std_Utlization_Mh, Avg_Utlization_Md, Std_Utlization_Md, Avg_Complete_Jobs, Std_Complete_Jobs
    
    def schedule(self, decisions):
        """
        Do schedule work
        """
        Job_idx, Mould_idx, Machine_idx = decisions[0], decisions[1], decisions[2]
        operation_end_time = max(0, self.job_arrive_list[Job_idx])
        mould_end_time = max(self.moulds[Mould_idx].End) if len(self.moulds[Mould_idx].End) > 0 else 0
        machine_end_time = max(self.machines[Machine_idx].End) if len(self.machines[Machine_idx].End) > 0 else 0
        machine_end_time_prime = 0
        for x in self.machines[Machine_idx].Change_mould + self.machines[Machine_idx].Change_colour:
            if x[1] > machine_end_time_prime:
                machine_end_time_prime = x[1]
        mould_end_time_prime = 0
        for x in self.moulds[Mould_idx].Change_mold + self.moulds[Mould_idx].Change_colour:
            if x[1] > mould_end_time_prime:
                mould_end_time_prime = x[1]

        start_time = max(operation_end_time, mould_end_time, machine_end_time, machine_end_time_prime, mould_end_time_prime)
        PT = self.processing_time[Job_idx][Mould_idx][Machine_idx]
        assert PT>0

        Job_color = self.jobs[Job_idx].job_colour
        Mould_type = self.moulds_types[Mould_idx]
        Mould_current_machine = self.moulds[Mould_idx].curr_machine

        Jobs_assign_for_machine = self.machines[Machine_idx].job_assign_for
        if len(Jobs_assign_for_machine)>0:
            Previous_job = Jobs_assign_for_machine[-1]
            Previous_color = self.jobs[Previous_job].job_colour
        else:
            Previous_color = self.machines[Machine_idx].init_colour
        Machine_curr_mould = self.machines[Machine_idx].curr_mould
        if Machine_curr_mould == None:
            Previous_mould_type = None
        else:
            Previous_mould_type = self.moulds_types[Machine_curr_mould]

        Time_add = 0
        if Mould_type != Previous_mould_type:
            Time_add = 8
            self.machines[Machine_idx].curr_mould = Mould_idx
            self.machines[Machine_idx].Change_mould.append([start_time, start_time+8])
            self.moulds[Mould_idx].curr_machine = Machine_idx
            self.moulds[Mould_idx].Change_mould.append([start_time, start_time+8])
            if Machine_curr_mould != None:
                self.machines[Mould_current_machine].curr_mould = None 
                self.machines[Mould_current_machine].Change_mould.append([start_time, start_time+8])
            if Mould_current_machine != None:
                self.moulds[Machine_curr_mould].curr_machine = None
                self.moulds[Machine_curr_mould].Change_mould.append([start_time, start_time+8])
        elif Job_color != Previous_color:
            Time_add = 1
            self.machines[Mould_current_machine].Change_colour.append([start_time, start_time+1])
            self.moulds[Machine_curr_mould].Change_colour.append([start_time, start_time+1])

        start_time += Time_add
        end_time = start_time + PT
        assert start_time != float("inf")
        assert end_time != float("inf")

        self.jobs[Job_idx]._assign(start_time, end_time, Mould_idx, Machine_idx, PT)
        self.moulds[Mould_idx]._add_job(start_time, end_time, Job_idx, Machine_idx, PT)
        self.machines[Machine_idx]._add_job(start_time, end_time, Job_idx, Mould_idx, PT)

        # Update
        assert len(self.machines[Machine_idx].End) > 0
        assert len(self.moulds[Mould_idx].End) > 0
        self.compleMean_C_J_time_endMh[Machine_idx] = max(self.machines[Machine_idx].End)
        self.utilization_Mh[Machine_idx] = sum(self.machines[Machine_idx].T)/self.compleMean_C_J_time_endMh[Machine_idx]
        self.compleMean_C_J_time_endMd[Mould_idx] = max(self.moulds[Mould_idx].End)
        self.utilization_Md[Mould_idx] = sum(self.moulds[Mould_idx])
        self.complete_procedures_J[Job_idx] += 1
        assert self.complete_procedures_J[Job_idx] <= 1

    def construct_scene(self):
        """
        Construct APS Scene
        """
        self.jobs_num, self.moulds_num, self.machines_num, self.processing_time, self.job_arrive_list, self.job_delivery_list, \
            self.job_colors, self.moulds_types, self.machine_init_moulds, self.machine_init_colors = self.instance_generator()
        self.compleMean_C_J_time_endMh = np.zeros(self.machines_num)  #各机器最后一道工序完工时间
        self.utilization_Mh = np.zeros(self.machines_num)   #机器利用率
        self.compleMean_C_J_time_endMd = np.zeros(self.moulds_num)    #各模具最后一道工序完工时间
        self.utilization_Md = np.zeros(self.moulds_num) #模具利用率
        self.complete_procedures_J = np.zeros(self.jobs_num)    #各工件的已加工工序数列表

        self.jobs = [Object_job(i, self.job_colors[i]) for i in range(self.jobs_num)]
        self.machines = [Object_machine(i, self.machine_init_moulds[i], self.machine_init_colors[i]) for i in range(self.machines_num)]
        self.moulds = [Object_mould(i, np.argwhere(self.machine_init_moulds==i)) \
                      if i in self.machine_init_moulds else Object_mould(i, None) for i in range(self.moulds_num)]

    def instance_generator(self):
        """
        Generate instance for APS
        """
        Jobs_num = np.random.randint(self.parameters["min_jobs"], self.parameters["max_jobs"])
        Moulds_num = self.parameters["moulds_num"]
        Machines_num = np.random.randint(self.parameters["min_machines"], self.parameters["max_machines"])

        Processing_time = []
        for J_idx in range(Jobs_num):
            correspond_moulds_num = np.random.randint(self.parameters["min_corr_moulds"], self.parameters["max_corr_moulds"])
            correspond_moulds = np.random.choice(list(range(Moulds_num)),correspond_moulds_num)
            moulds = np.zeros(Moulds_num, dtype=list)
            for Mould in correspond_moulds:
                correspond_machines_num = np.random.randint(self.parameters["min_corr_machines"], self.parameters["max_corr_machines"])
                correspond_machines = np.random.choice(list(range(Machines_num)), correspond_machines_num)
                machines = np.zeros(Machines_num)
                pass_time = np.random.uniform(low=1, high=self.parameters["Ptime_coefficient"])
                for Machine in correspond_machines:
                    machines[Machine] = int(pass_time)
                moulds[Mould] = machines
            Processing_time.append(moulds)

        J_Arrive_list = np.zeros(Jobs_num)
        J_Delivery_list = np.array([np.random.normal(0.5, 0.2, Jobs_num)*(24*15) for _ in range(Jobs_num)])

        Job_colors = np.array([int(np.random.uniform(low=0, high=self.parameters["Jcolor_coefficient"])) for _ in range(Jobs_num)])
        Moulds_types = np.array([int(np.random.uniform(low=0, high=self.parameters["Mtypes_coefficient"])) for _ in range(Moulds_num)])

        Machine_init_moulds = np.random.choice(list(range(Moulds_num)), Machines_num)
        Machine_init_colors = np.array([int(np.random.uniform(low=0, high=self.parameters["Mcolor_coefficient"])) for _ in range(Machines_num)])
        
        # 订单数，模具数，机器数，订单对应工序对应机器对应执行时间，订单到达时间，订单交付时间，订单颜色，模具类型，机器初始模具，机器初始颜色
        return Jobs_num, Moulds_num, Machines_num, Processing_time, J_Arrive_list, J_Delivery_list, Job_colors, Moulds_types, Machine_init_moulds, Machine_init_colors

    def render(self):
        pass    


if __name__ == "__main__":
    with open("./config.yaml", "r", encoding="utf-8") as f:
        parameters = yaml.load(f.read(), Loader=yaml.FullLoader)
    print(parameters)
    env = JSSPEnv(parameters)
    env.construct_scene()
    print("Finished Test")