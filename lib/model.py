import torch
from torch import nn

class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()


    def prep(self,obs):
        # team info
        my_team_info=obs['my_team']
        for_team_info=obs['foe_team']

