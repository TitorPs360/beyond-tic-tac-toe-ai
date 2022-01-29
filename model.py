import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

DEVICE = 'cuda'

class Linear_QNet(nn.Module):
    def __init__(self, input_size, output_size):
        super().__init__()
        self.input_layer = nn.Linear(input_size, 256)
        self.dl1 = nn.Linear(256, 256)
        self.output_layer = nn.Linear(256, output_size)

    def forward(self, x):
        x = x.to(DEVICE)

        x = self.input_layer(x)
        x = torch.relu(x)

        x = self.dl1(x)
        x = torch.relu(x)

        x = self.output_layer(x)
        x = torch.sigmoid(x)
        
        return x

    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float).to(DEVICE)
        next_state = torch.tensor(next_state, dtype=torch.float).to(DEVICE)
        action = torch.tensor(action, dtype=torch.long).to(DEVICE)
        reward = torch.tensor(reward, dtype=torch.float).to(DEVICE)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0).to(DEVICE)
            next_state = torch.unsqueeze(next_state, 0).to(DEVICE)
            action = torch.unsqueeze(action, 0).to(DEVICE)
            reward = torch.unsqueeze(reward, 0).to(DEVICE)
            done = (done, )

        pred = self.model(state)

        target = pred.clone()

        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx])).to(DEVICE)

            target[idx][action[idx]] = Q_new

        # backpropagate
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()
