import numpy as np
from collections import deque
import random

class ReplayBuffer:
    def __init__(self, size, obs_dim, act_dim, num_agents):
        """初始化回放缓冲区。

        Args:
            size (int): 缓冲区最大容量。
            obs_dim (int): 每个智能体的观察维度。
            act_dim (int): 每个智能体的动作维度。
            num_agents (int): 智能体数量。
        """
        self.size = size
        self.num_agents = num_agents
        self.memory = deque(maxlen=size)
        self.obs_dim = obs_dim
        self.act_dim = act_dim

    def add(self, state, obs, actions, rewards, next_state, dones):
        """添加经验到缓冲区。

        Args:
            state (np.ndarray): 全局状态。
            obs (list): 每个智能体的观察列表。
            actions (list): 每个智能体的动作列表。
            rewards (list): 每个智能体的奖励列表。
            next_state (np.ndarray): 下一全局状态。
            dones (list): 每个智能体的终止标志列表。
        """
        experience = (state, obs, actions, rewards, next_state, dones)
        self.memory.append(experience)

    def sample(self, batch_size):
        """从缓冲区中随机采样一批经验。

        Args:
            batch_size (int): 采样批次大小。

        Returns:
            tuple: (states, obs, actions, rewards, next_states, dones) 的批量数据。
        """
        batch = random.sample(self.memory, batch_size)
        states = np.array([exp[0] for exp in batch])
        obs = [np.array([exp[1][i] for exp in batch]) for i in range(self.num_agents)]
        actions = [np.array([exp[2][i] for exp in batch]) for i in range(self.num_agents)]
        rewards = [np.array([exp[3][i] for exp in batch]) for i in range(self.num_agents)]
        next_states = np.array([exp[4] for exp in batch])
        dones = [np.array([exp[5][i] for exp in batch]) for i in range(self.num_agents)]
        return states, obs, actions, rewards, next_states, dones

    def __len__(self):
        """返回缓冲区当前大小。"""
        return len(self.memory)

    def save(self, directory, episode):
        """保存 ReplayBuffer 的经验数据。

        Args:
            directory (str): 保存目录。
            episode (int): 当前 episode 编号。
        """
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, f'replay_buffer_episode_{episode}.pkl'), 'wb') as f:
            pickle.dump(self.memory, f)
        print(f"ReplayBuffer 已保存到 {directory}/replay_buffer_episode_{episode}.pkl")

    def load(self, directory, episode):
        """加载 ReplayBuffer 的经验数据。

        Args:
            directory (str): 保存目录。
            episode (int): 要加载的 episode 编号。
        """
        with open(os.path.join(directory, f'replay_buffer_episode_{episode}.pkl'), 'rb') as f:
            self.memory = pickle.load(f)
        print(f"ReplayBuffer 已从 {directory}/replay_buffer_episode_{episode}.pkl 加载")