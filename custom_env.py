import gym
import numpy as np
from gym import spaces
from typing import List, Tuple
import networkx as nx
import controller
from p4runtime_sh.shell import setup, TableEntry, teardown
import subprocess
import datetime
import time

class CompetitiveNetworkEnv(gym.Env):
    def __init__(self, num_agents: int):
        super(CompetitiveNetworkEnv, self).__init__()
        self.num_agents = num_agents
        
        # 动作空间：每个智能体输出三个整数 (a1, a2, a3)，满足 1 ≤ a1 < a2 < a3 ≤ 10000
        self.action_space = [spaces.MultiDiscrete([10000, 10000, 10000]) for _ in range(num_agents)]
        
        # 观察空间：每个智能体观察两个整数 (o1, o2)，o1 ∈ [1, 10240], o2 ∈ [1, 30]
        self.observation_space = [spaces.MultiDiscrete([10240, 30]) for _ in range(num_agents)]
        
        
        # 网络拓扑和节点信息（示例，具体实现需根据外部环境）
        self.graph = nx.Graph()  # 存储图结构
        self.interface_relations = {}
        self.node_to_index={}
        self.hosts={}
        self.switches={}
        self.graph =nx.Graph()
        self.pids={}
        # self.send_hosts=['h1','h2','h10','h12','h13','h18','h19']
        # self.receive_hosts=['h7','h15','h17','h13','h15','h11','h14']
        self.send_hosts=['h1','h2','h10','h12','h18','h19']
        self.receive_hosts=['h7','h15','h17','h13','h11','h14']
        self.graph, self.hosts, self.switches, self.node_to_index, self.interface_relations=controller.init_topology(self.graph, self.hosts, self.switches, self.node_to_index, self.interface_relations)

        default_paths0=[0,19,20,21,25,6]
        default_paths1=[7,25,26,27,8]
        default_paths2=[9,27,26,35,34,33,16]
        default_paths3=[17,34,35,29,28,10]
        default_paths4=[11,29,30,12]
        # default_paths5=[12,30,31,14]
        default_paths6=[18,35,31,13]
        default_paths7=[1,36,21,25,26,35,29,30,31,14]
        # self.default_paths=[default_paths0,default_paths1,default_paths2,default_paths3,default_paths4,default_paths5,default_paths6,default_paths7]
        self.default_paths=[default_paths0,default_paths1,default_paths2,default_paths3,default_paths4,default_paths6,default_paths7]
        self.pids=self.get_mininet_host_pids()
        # 智能体属性
        self.agents = [
            {
                "route": self.default_paths[i],      # 整数数组
                "pid":self.pids[self.send_hosts[i]], # 主机进程号
                "size": 1024                                # 整数
            } for i in range(num_agents)
        ]

    def get_mininet_host_pids(self):
        """
        查询所有 mininet 主机对应的进程 PID，返回字典 {host: pid}
        """
        try:
            # 执行 ps 命令查询 mininet 主机相关的进程
            result = subprocess.run(
                "ps -eo pid,cmd | grep 'mininet:h' | grep -v grep",
                shell=True, capture_output=True, text=True
            )

            host_pid_map = {}
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.strip().split(None, 1)
                    pid = int(parts[0])
                    cmd = parts[1]
                    if '--norc' in cmd and 'mininet:h' in cmd:
                        # 提取主机名（如 mininet:h1）
                        for token in cmd.split():
                            if 'mininet:h' in token:
                                host = token.split(':')[1]
                                host_pid_map[host] = pid
            return host_pid_map

        except Exception as e:
            print("发生错误：", e)
            return {}

    def reset(self) -> List[np.ndarray]:
        # 重置环境
        self.chongzhi()
        # 获取初始观察
        observations = []
        for agent_id in range(self.num_agents):
            o1, o2 = self._get_observation(agent_id)
            observations.append(np.array([o1, o2], dtype=np.int32))
        
        return observations

    def _get_observation(self, agent_id: int) -> Tuple[int, int]:
        o1=len(self.default_paths[agent_id])
        o2=self.agents[agent_id]['size']
        return o1, o2

    def chongzhi(self):
        # 多个表或多个交换机
        print('开始重置')
        tables = ['MyIngress.ipv4_lpm', 'MyIngress.reroute_path','MyIngress.update_cost_tag']
        for i in range(0,18):
            self.clear_flow_tables(table=tables, device_id=i, grpc_addr='localhost:'+str(i+50051))

    def clear_flow_tables(self,table, device_id, grpc_addr):
        print('clear '+str(device_id))
        client=None
        try:
            client=setup(
                device_id=device_id, 
                grpc_addr=grpc_addr, 
                election_id=(0, 1))
            for table_name in table:
                table = TableEntry(table_name)
                for entry in table.read():
                    entry.delete()
            teardown()
        except Exception as e:
            print(f"错误: {e}")
            raise

    def step(self, actions: List[np.ndarray]) -> Tuple[List[np.ndarray], List[float], List[bool], dict]:
        # actions: 每个智能体的动作，形如 [[a1, a2, a3], ...]
        rewards = []
        observations = []
        dones = [False] * self.num_agents
        info = {}
        
        for agent_id, action in enumerate(actions):
            a1, a2, a3 = action
            # 执行动作
            self.xingdong(a1, a2, a3)
        
            
            # 获取观察（示例，实际需调用外部函数）
            o1=len(self.agents[agent_id]['route'])
            o2=self.agents[agent_id]['size']
            observations.append(np.array([o1, o2], dtype=np.int32))

        self.ceshi()

        for agent_id in range(self.num_agents):
            delay=self.calculate_average_delay('/home/p4/tutorials/exercises/myp4/receive'+self.send_hosts[agent_id]+'.drc')
            rewards.append(0-delay)
        # 判断是否终止（根据实际需求定义，例如最大步数）
        # 示例：假设固定步数后终止
        # if some_condition:  # 替换为实际终止条件
        #     dones = [True] * self.num_agents
        
        return observations, rewards, dones, info

    def ceshi(self):
        receive_progress = []
        for i in range(self.num_agents) :
            print(self.receive_hosts[i]+'开始监听')
            receive_pid=self.pids[self.receive_hosts[i]]
            # receive_cmd=f"sudo mnexec -a {receive_pid} mgen input listen.mgn output /home/p4/tutorials/exercises/myp4/{self.send_hosts[i]}.drc"
            receive_cmd = ["sudo","mnexec", "-a", str(receive_pid) , "timeout", "185", "mgen", "input", "/home/p4/tutorials/exercises/myp4/listen.mgn", "output", "/home/p4/tutorials/exercises/myp4/receive"+self.send_hosts[i]+".drc"]
            p=subprocess.Popen(receive_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            receive_progress.append(p) 
        for i in range(self.num_agents) :
            print(self.send_hosts[i]+'开始发送')
            send_pid=self.pids[self.send_hosts[i]]
            # send_cmd = f"sudo mnexec -a {send_pid} mgen nolog input /home/p4/tutorials/exercises/myp4/{send_hosts[i]}.mgn"
            send_cmd = ["sudo" , "mnexec", "-a", str(send_pid), "mgen", "nolog", "input", "/home/p4/tutorials/exercises/myp4/"+self.send_hosts[i]+".mgn"]
            p=subprocess.Popen(send_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(190)



    def calculate_average_delay(self,file_path):
        """
        读取文件内容，计算延迟并返回平均延迟和延迟列表。
        
        :param file_path: 文件路径
        :return: (平均延迟, 延迟列表)
        """
        def parse_timestamp(timestamp):
            return datetime.datetime.strptime(timestamp, '%H:%M:%S.%f')

        def calculate_delay(recv_time, send_time):
            recv_dt = parse_timestamp(recv_time)
            send_dt = parse_timestamp(send_time)
            delay = (recv_dt - send_dt).total_seconds()
            return delay

        send_times = []
        delays = []
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines[2:-1]:  # 跳过前两行和最后一行
                recv_time = line.split(' ')[0]
                send_time = line.split('sent>')[1].split(' ')[0]
                delay = calculate_delay(recv_time, send_time)
                send_times.append(parse_timestamp(send_time))
                delays.append(delay * 1000)  # 转换为毫秒

        # 计算相对发送时间
        start_time = send_times[0]
        relative_send_times = [(t - start_time).total_seconds() for t in send_times]

        # 筛选时间范围内的延迟
        filtered_delays = [
            delay for time, delay in zip(relative_send_times, delays) if 20 <= time <= 160
        ]

        # 计算平均延迟
        avg_delay = sum(filtered_delays) / len(filtered_delays) if filtered_delays else 0
        print(file_path+'平均延迟为：'+str(avg_delay))

        return avg_delay

    def xingdong(self,a1,a2,a3):
        print('开始行动')
        controller.main('./build/advanced_tunnel.p4.p4info.txtpb','./build/advanced_tunnel.json',a1,a2,a3)

    def close(self):
        # 清理资源
        self.chongzhi()

