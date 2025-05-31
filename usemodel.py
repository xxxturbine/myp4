import torch
import numpy as np
from maddpg import MADDPG
from custom_env import CompetitiveNetworkEnv
import os

# 参数设置（与训练时一致）
num_agents = 6
obs_dim = 2
act_dim = 3
state_dim = 18  # 调整为 18 以匹配保存的模型
model_dir = "models"
episode_to_load = 4  # 要加载的 episode 编号

# 验证输入维度
input_dim = state_dim + num_agents * (obs_dim + act_dim)
print(f"SharedCritic input dimension: {input_dim}")  # 应为 53

# 初始化环境
env = CompetitiveNetworkEnv(num_agents=num_agents)

# 初始化 MADDPG
maddpg = MADDPG(
    num_agents=num_agents,
    obs_dim=obs_dim,
    act_dim=act_dim,
    state_dim=state_dim,
    lr=1e-3,
    gamma=0.99,
    tau=0.01
)

best_i=0
best_r=100

def test():
    global best_i,best_r
    # 测试模型（推理）
    # num_episodes = 1
    # for episode in range(num_episodes):
    obs = env.reset()
    episode_rewards = [0.0] * num_agents
    done = False
    step = 0
    # while not done and step < 100:
    actions = maddpg.select_actions(obs)
    next_obs, rewards, dones, info = env.step(actions)

    obs = next_obs
    episode_rewards = [r + er for r, er in zip(rewards, episode_rewards)]
    if best_r>(0-rewards[1]):
        best_i=i+1
        best_r=0-rewards[1]
    done = any(dones)
    step += 1

    # print(f"Test Episode {episode}, Rewards: {episode_rewards}")

    # 关闭环境
    env.close()


for i in range(24):
    episode_to_load=i+1
    # 加载模型
    try:
        maddpg.load(model_dir, episode_to_load)
        print(f"成功加载模型（Episode {episode_to_load}）")
    except FileNotFoundError as e:
        print(f"错误：无法找到模型文件：{e}")
        exit(1)
    except RuntimeError as e:
        print(f"错误：加载模型失败：{e}")
        exit(1)
    
    # 设置为评估模式
    for actor in maddpg.actors:
        actor.eval()
    maddpg.critic.eval()
    test()
print(str(best_i)+' '+str(best_r))