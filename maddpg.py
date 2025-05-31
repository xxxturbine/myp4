import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import os

class Actor(nn.Module):
    def __init__(self, obs_dim, act_dim):
        super(Actor, self).__init__()
        self.fc1 = nn.Linear(obs_dim, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, act_dim)

    def forward(self, obs):
        x = F.relu(self.fc1(obs))
        x = F.relu(self.fc2(x))
        x = torch.tanh(self.fc3(x)) * 10000
        return x

class SharedCritic(nn.Module):
    def __init__(self, state_dim, obs_dim, act_dim, num_agents):
        super(SharedCritic, self).__init__()
        self.fc1 = nn.Linear(state_dim + num_agents * (obs_dim + act_dim), 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, num_agents)  # 输出每个智能体的 Q 值

    def forward(self, state, obs, actions):
        x = torch.cat([state] + obs + actions, dim=1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        q_values = self.fc3(x)  # [batch_size, num_agents]
        return q_values

class MADDPG:
    def __init__(self, num_agents, obs_dim, act_dim, state_dim, lr=1e-3, gamma=0.99, tau=0.01):
        self.num_agents = num_agents
        self.gamma = gamma
        self.tau = tau

        self.actors = [Actor(obs_dim, act_dim) for _ in range(num_agents)]
        self.critic = SharedCritic(state_dim, obs_dim, act_dim, num_agents)  # 共享 Critic
        self.target_actors = [Actor(obs_dim, act_dim) for _ in range(num_agents)]
        self.target_critic = SharedCritic(state_dim, obs_dim, act_dim, num_agents)

        self.actor_optimizers = [optim.Adam(actor.parameters(), lr=lr) for actor in self.actors]
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=lr)

        for i in range(num_agents):
            self.target_actors[i].load_state_dict(self.actors[i].state_dict())
        self.target_critic.load_state_dict(self.critic.state_dict())

    def select_actions(self, obs):
        actions = []
        for i, agent_obs in enumerate(obs):
            agent_obs = torch.FloatTensor(agent_obs).unsqueeze(0)
            action = self.actors[i](agent_obs).detach().numpy()[0]
            action = np.clip(action, 1, 10000)
            sorted_action = np.sort(action)
            a1, a2, a3 = sorted_action
            if a1 >= a2 or a2 >= a3:
                a1 = np.random.randint(1, 3334)
                a2 = np.random.randint(a1 + 1, 6667)
                a3 = np.random.randint(a2 + 1, 10001)
            action = [int(a1), int(a2), int(a3)]
            actions.append(action)
        return actions

    def update(self, batch):
        states, obs, actions, rewards, next_states, dones = batch
        states = torch.FloatTensor(states)
        next_states = torch.FloatTensor(next_states)

        # 计算所有智能体的 Q 值
        all_obs = [torch.FloatTensor(obs[i]) for i in range(self.num_agents)]
        all_actions = [torch.FloatTensor(actions[i]) for i in range(self.num_agents)]
        all_rewards = [torch.FloatTensor(rewards[i]).unsqueeze(1) for i in range(self.num_agents)]
        all_dones = [torch.FloatTensor(dones[i]).unsqueeze(1) for i in range(self.num_agents)]

        # 目标 Q 值
        next_actions = [self.target_actors[i](all_obs[i]) for i in range(self.num_agents)]
        target_qs = self.target_critic(next_states, all_obs, next_actions)  # [batch_size, num_agents]
        target_qs = [target_qs[:, i].unsqueeze(1) for i in range(self.num_agents)]
        target_qs = [all_rewards[i] + self.gamma * target_qs[i] * (1 - all_dones[i]) for i in range(self.num_agents)]

        # 当前 Q 值
        current_qs = self.critic(states, all_obs, all_actions)  # [batch_size, num_agents]
        critic_loss = sum(F.mse_loss(current_qs[:, i].unsqueeze(1), target_qs[i].detach()) for i in range(self.num_agents))

        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()

        for i in range(self.num_agents):
            predicted_actions = [self.actors[j](all_obs[j]) if j == i else all_actions[j] for j in range(self.num_agents)]
            actor_loss = -self.critic(states, all_obs, predicted_actions)[:, i].mean()

            self.actor_optimizers[i].zero_grad()
            actor_loss.backward()
            self.actor_optimizers[i].step()

        for target_param, param in zip(self.target_critic.parameters(), self.critic.parameters()):
            target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)
        for i in range(self.num_agents):
            for target_param, param in zip(self.target_actors[i].parameters(), self.actors[i].parameters()):
                target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)

    def save(self, directory, episode):
        os.makedirs(directory, exist_ok=True)
        for i in range(self.num_agents):
            torch.save(self.actors[i].state_dict(), os.path.join(directory, f'actor_agent_{i}_episode_{episode}.pth'))
            torch.save(self.target_actors[i].state_dict(), os.path.join(directory, f'target_actor_agent_{i}_episode_{episode}.pth'))
        torch.save(self.critic.state_dict(), os.path.join(directory, f'critic_episode_{episode}.pth'))
        torch.save(self.target_critic.state_dict(), os.path.join(directory, f'target_critic_episode_{episode}.pth'))

    def load(self, directory, episode):
        for i in range(self.num_agents):
            print(f'load actor_agent_{i}_episode_{episode}.pth')
            print(f'load target_actor_agent_{i}_episode_{episode}.pth')
            self.actors[i].load_state_dict(torch.load(os.path.join(directory, f'actor_agent_{i}_episode_{episode}.pth')))
            self.target_actors[i].load_state_dict(torch.load(os.path.join(directory, f'target_actor_agent_{i}_episode_{episode}.pth')))
        print(f'load critic_episode_{episode}.pth')
        print(f'load target_critic_episode_{episode}.pth')
        self.critic.load_state_dict(torch.load(os.path.join(directory, f'critic_episode_{episode}.pth')))
        self.target_critic.load_state_dict(torch.load(os.path.join(directory, f'target_critic_episode_{episode}.pth')))
