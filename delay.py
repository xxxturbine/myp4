import datetime
import matplotlib.pyplot as plt
import os
def parse_timestamp(timestamp):
    return datetime.datetime.strptime(timestamp, '%H:%M:%S.%f')

def calculate_delay(recv_time, send_time):
    recv_dt = parse_timestamp(recv_time)
    send_dt = parse_timestamp(send_time)
    delay = (recv_dt - send_dt).total_seconds()
    return delay

def extract_times_and_calculate_delays(file_path):
    send_times = []
    delays = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines[2:-1]:
            recv_time = line.split(' ')[0]
            send_time = line.split('sent>')[1].split(' ')[0]
            delay = calculate_delay(recv_time, send_time)
            send_times.append(parse_timestamp(send_time))
            delays.append(delay*1000)
    return send_times, delays

def plot_delays(send_times, delays):
    
    start_time = send_times[0]
    relative_send_times = [(t - start_time).total_seconds() for t in send_times]
    filtered_send_times = []
    filtered_delays = []
    for time, delay in zip(relative_send_times, delays):
        if 20 <= time <= 160:
            filtered_send_times.append(time)
            filtered_delays.append(delay)
    avg=sum(filtered_delays)/len(filtered_delays)
    print(avg)
    
    # plt.switch_backend('Agg')  # 注释掉这行，因为Agg后端不支持显示
    plt.scatter(filtered_send_times, filtered_delays, s=4)
    plt.xlabel('Send Time (s)')
    plt.ylabel('Delay (ms)')
    plt.title('Delay vs. Send Time')
    
    # 创建保存图像的目录
    save_dir = os.path.join('/mnt/hgfs/newp4', str(avg))
    os.makedirs(save_dir, exist_ok=True)
    
    plt.show()
    save_path = os.path.join(save_dir, '1.png')
    plt.savefig(save_path)

if __name__ == "__main__":
    file_path = 'D:\\newp4\\2.drc'
    send_times, delays = extract_times_and_calculate_delays(file_path)
    plot_delays(send_times, delays)
