import controller
import networkx as nx
from mininet.net import Mininet

# interface_relations = {}
# node_to_index={}
# hosts={}
# switches={}
# graph = nx.Graph()
# graph, hosts, switches, node_to_index, interface_relations=controller.init_topology(graph, hosts, switches, node_to_index, interface_relations)
# print(node_to_index)
# print(interface_relations)
# print("--------------------------------")
# print(node_to_index)
# print("--------------------------------")
# print(graph)
# print("--------------------------------")
# print(hosts['h1'])
# print("--------------------------------")
# print(switches)
# print("--------------------------------")
# def run_command(self,host, cmd):
#     print(f'Running command on {host.name}')
#     result = host.cmd(cmd)
#     print('--------'+host.name+'---------\n')
#     print(result)

"""
sudo PATH=/home/p4/tutorials/vm-ubuntu-24.04:/home/p4/src/behavioral-model/tools:/usr/local/bin:/home/p4/src/p4dev-python-venv/bin:/home/p4/.vscode-server/cli/servers/Stable-17baf841131aa23349f217ca7c570c76ee87b957/server/bin/remote-cli:/home/p4/tutorials/vm-ubuntu-24.04:/home/p4/src/behavioral-model/tools:/usr/local/bin:/home/p4/src/p4dev-python-venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/home/p4/.vscode-server/data/User/globalStorage/github.copilot-chat/debugCommand PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python python3 /home/p4/tutorials/exercises/myp4/testcode.py
"""



# import subprocess
# import time

# def get_mininet_host_pids():
#     """
#     查询所有 mininet 主机对应的进程 PID，返回字典 {host: pid}
#     """
#     try:
#         # 执行 ps 命令查询 mininet 主机相关的进程
#         result = subprocess.run(
#             "ps -eo pid,cmd | grep 'mininet:h' | grep -v grep",
#             shell=True, capture_output=True, text=True
#         )

#         host_pid_map = {}
#         for line in result.stdout.strip().split('\n'):
#             if line:
#                 parts = line.strip().split(None, 1)
#                 pid = int(parts[0])
#                 cmd = parts[1]
#                 if '--norc' in cmd and 'mininet:h' in cmd:
#                     # 提取主机名（如 mininet:h1）
#                     for token in cmd.split():
#                         if 'mininet:h' in token:
#                             host = token.split(':')[1]
#                             host_pid_map[host] = pid
#         return host_pid_map

#     except Exception as e:
#         print("发生错误：", e)
#         return {}


# # 示例使用
# if __name__ == "__main__":
#     host_pids = get_mininet_host_pids()
#     print("主机和对应的 PID：", host_pids)
#     progress = []
#     h1=host_pids['h1']
#     h2=host_pids['h7']
#     cmd1=["sudo","mnexec", "-a", str(h2) ,"timeout" , "185" , "mgen","input", "/home/p4/tutorials/exercises/myp4/listen.mgn" , "output", "/home/p4/tutorials/exercises/myp4/receiveh1.drc"]
    
#     cmd2=["sudo","mnexec", "-a", str(h1) , "mgen","input", "/home/p4/tutorials/exercises/myp4/h1.mgn"]
#     # 命令 1：例如发送数据包
#     subprocess.Popen(cmd1, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#     subprocess.Popen(cmd2, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#     time.sleep(190)


    # for host, pid in host_pids.items():
    #     pid = host_pids[host]
    #     # cmd = f"sudo mnexec -a {pid} mgen input /home/p4/tutorials/exercises/myp4/listen.mgn"
    #     # cmd = ["sudo", "mnexec", "-a", str(pid), "mgen", "input", "/home/p4/tutorials/exercises/myp4/listen.mgn"]
        
    #     cmd = ["sudo","mnexec", "-a", str(pid),"timeout","10", "ping","baidu.com"]
    #     print(cmd)
    #     p=subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    #     progress.append(p)
    # for p in progress :
    #     print('杀掉',p.pid)
    #     p.terminate()


# import controller
# controller.main('./build/advanced_tunnel.p4.p4info.txtpb','./build/advanced_tunnel.json',3000,5000,7000)


# from p4runtime_sh.shell import setup, TableEntry,teardown

# def clear_flow_tables(tables, device_id, grpc_addr):
#     try:
#         client=setup(
#             device_id=device_id, 
#             grpc_addr=grpc_addr, 
#             election_id=(0, 1))
#         for table_name in tables:
#             table = TableEntry(table_name)
#             for entry in table.read():
#                 print(f"正在删除表项 ({table_name}): {entry}")
#                 entry.delete()
#             print(f"s{device_id+1}流表 {table_name} 已清除")
#         teardown()
#     except Exception as e:
#         print(f"错误: {e}")
#         raise

# if __name__ == '__main__':
#     # 多个表或多个交换机
#     tables = ['MyIngress.ipv4_lpm', 'MyIngress.reroute_path','MyIngress.update_cost_tag']
#     clear_flow_tables(tables, 12, 'localhost:50063')
    # for i in range(0,18):
    #     clear_flow_tables(tables, i, 'localhost:'+str(i+50051))


# import datetime

# def calculate_average_delay(file_path):
#     """
#     读取文件内容，计算延迟并返回平均延迟和延迟列表。
    
#     :param file_path: 文件路径
#     :return: (平均延迟, 延迟列表)
#     """
#     def parse_timestamp(timestamp):
#         return datetime.datetime.strptime(timestamp, '%H:%M:%S.%f')

#     def calculate_delay(recv_time, send_time):
#         recv_dt = parse_timestamp(recv_time)
#         send_dt = parse_timestamp(send_time)
#         delay = (recv_dt - send_dt).total_seconds()
#         return delay

#     send_times = []
#     delays = []
#     print('计算延迟')
#     with open(file_path, 'r') as file:
#         lines = file.readlines()
#         for line in lines[2:-1]:  # 跳过前两行和最后一行
#             recv_time = line.split(' ')[0]
#             send_time = line.split('sent>')[1].split(' ')[0]
#             delay = calculate_delay(recv_time, send_time)
#             send_times.append(parse_timestamp(send_time))
#             delays.append(delay * 1000)  # 转换为毫秒

#     # 计算相对发送时间
#     start_time = send_times[0]
#     relative_send_times = [(t - start_time).total_seconds() for t in send_times]

#     # 筛选时间范围内的延迟
#     filtered_delays = [
#         delay for time, delay in zip(relative_send_times, delays) if 20 <= time <= 160
#     ]

#     # 计算平均延迟
#     avg_delay = sum(filtered_delays) / len(filtered_delays) if filtered_delays else 0

#     return avg_delay
# delay=calculate_average_delay('/home/p4/tutorials/exercises/myp4/receiveh2.drc')
# print(delay)

# import subprocess
# import os

# def run_mnexec_command(host_pid, command):
#     """在 Mininet 主机上非阻塞运行命令。

#     Args:
#         host_pid (int): 主机的 PID。
#         command (str): 要执行的命令。
#     Returns:
#         subprocess.Popen: 进程对象。
#     """
#     mnexec_cmd = f"sudo mnexec -a {host_pid} {command}"
#     process = subprocess.Popen(
#         mnexec_cmd,
#         shell=True,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         text=True
#     )
#     return process

# """示例：同时在主机上运行两个命令"""
# host_pid = 4162  # 替换为实际 PID（从 env.pids 获取）

# # 命令 1：例如发送数据包
# cmd1 = f"iperf -c 10.0.0.2 -t 10"  # 示例命令
# process1 = run_mnexec_command(host_pid, cmd1)

# # 命令 2：例如运行监控脚本
# cmd2 = f"ping 10.0.0.2 -c 4"  # 示例命令
# process2 = run_mnexec_command(host_pid, cmd2)

# # 可选：等待进程完成并获取输出
# stdout1, stderr1 = process1.communicate()
# stdout2, stderr2 = process2.communicate()

# if process1.returncode != 0:
#     print(f"命令 1 失败: {stderr1}")
# if process2.returncode != 0:
#     print(f"命令 2 失败: {stderr2}")

# import p4runtime_sh.shell as sh

# try:
#     client = sh.setup(
#         device_id=12,
#         grpc_addr='localhost:50063',
#         election_id=(0, 1)
#     )
#     print("连接成功")
#     sh.teardown()
# except Exception as e:
#     print(f"测试错误: {e}")

"""
计算平均延迟以及画图
"""
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def draw(path):
    # Read the file, skipping the first 2 lines
    with open(path, 'r') as file:
        lines = file.readlines()[2:-1]  # Skip first 2 lines and last line

    # Parse the data
    data = []
    for line in lines:
        if 'RECV' not in line:
            continue
        parts = line.strip().split()
        recv_time_str = parts[0]
        # Find sent time by splitting on 'sent>' and taking the next part
        for part in parts:
            if part.startswith('sent>'):
                sent_time_str = part.split('sent>')[1]
                break
            if part.startswith('seq>'):
                seq = int(part.split('seq>')[1]) 
                continue
        
        # Convert time strings to datetime
        recv_time = datetime.strptime(recv_time_str, '%H:%M:%S.%f')
        sent_time = datetime.strptime(sent_time_str, '%H:%M:%S.%f')
        
        # Calculate latency in milliseconds
        latency = (recv_time - sent_time).total_seconds() * 1000
        data.append({'recv_time': recv_time, 'seq': seq, 'latency': latency})

    # Create DataFrame
    df = pd.DataFrame(data)

    # Convert recv_time to seconds since start for filtering
    start_time = df['recv_time'].min()
    df['time_since_start'] = (df['recv_time'] - start_time).dt.total_seconds()

    # Filter out first and last 20 seconds
    total_duration = df['time_since_start'].max()
    filtered_df = df[(df['time_since_start'] >= 20) & (df['time_since_start'] <= total_duration - 20)]

    # Calculate average latency
    if filtered_df.empty:
        print("Error: filtered_df is empty. No data remains after filtering.")
        return
    avg_latency = filtered_df['latency'].mean(skipna=True)

    # Print average latency
    print(f"Average Latency: {avg_latency:.2f} ms")

    # Create scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(filtered_df['seq'], filtered_df['latency'], alpha=0.5)
    plt.title('Latency vs Sequence Number')
    plt.xlabel('Sequence Number')
    plt.ylabel('Latency (ms)')
    plt.grid(True)

    # Save the plot
    plt.savefig(path+'.png')
draw('receiveh2.drc')

