from maddpg import MADDPG
from replay_buffer import ReplayBuffer
import os
from custom_env import CompetitiveNetworkEnv

env = CompetitiveNetworkEnv(num_agents=6)
maddpg = MADDPG(num_agents=6, obs_dim=2, act_dim=3, state_dim=3 * 6)
buffer = ReplayBuffer(size=1000000, obs_dim=2, act_dim=3, num_agents=6)

# 保存模型的目录
model_dir = "models"
os.makedirs(model_dir, exist_ok=True)
save_interval = 1  # 每 100 个 episode 保存一次模型

reward_dir = "rewards"
os.makedirs(reward_dir, exist_ok=True)
# 为每个智能体创建奖励文件
reward_files = [os.path.join(reward_dir, f"agent_{i}_rewards.txt") for i in range(env.num_agents)]
for episode in range(10000):
    obs = env.reset()
    episode_rewards = [0.0] * env.num_agents
    done = False
    step = 0
    while not done and step < 10:  # 最大步数限制
        actions = maddpg.select_actions(obs)
        next_obs, rewards, dones, info = env.step(actions)
        global_state = [
            [agent["pid"], agent["size"], len(agent["route"])]
            for agent in env.agents
        ]
        next_global_state = global_state  # 假设状态不变，或根据需要更新
        buffer.add(global_state, obs, actions, rewards, next_global_state, dones)
        
        obs = next_obs
        episode_rewards = [r + er for r, er in zip(rewards, episode_rewards)]
        done = any(dones)
        step += 1
        
    # 记录每个智能体的奖励到文件
        for i, reward in enumerate(episode_rewards):
            with open(reward_files[i], 'a') as f:
                f.write(f"{episode},{reward}\n")
        
        if len(buffer) > 1000:
            batch = buffer.sample(batch_size=128)
            maddpg.update(batch)
    
    
    print(f"Episode {episode}, Rewards: {episode_rewards}")
        # 每 save_interval 个 episode 保存模型

    if (episode + 1) % save_interval == 0:
        maddpg.save(model_dir, episode + 1)
        print(f"模型已保存到 {model_dir},Episode {episode + 1}")
