from globals import *
from algs.test_mst_alg import test_mst_alg
from functions import *


class RandomMstAlgAgent:
    def __init__(self, sim_agent):
        self.sim_agent = sim_agent
        self.name = self.sim_agent.name
        self.pos = self.sim_agent.pos
        self.nodes_dict = self.sim_agent.nodes_dict


class RandomMstAlg:
    def __init__(self):
        self.name = 'random'
        self.agents, self.agents_dict = None, None

    def create_entities(self, sim_agents, sim_targets, sim_nodes):
        self.agents, self.agents_dict = [], {}
        for sim_agent in sim_agents:
            new_agent = RandomMstAlgAgent(sim_agent)
            self.agents.append(new_agent)
            self.agents_dict[sim_agent.name] = new_agent

    def reset(self, sim_agents, sim_targets, sim_nodes):
        self.create_entities(sim_agents, sim_targets, sim_nodes)

    def get_actions(self):
        actions = {}
        for agent in self.agents:
            next_pos_name = random.choice(agent.pos.neighbours)
            next_pos = agent.nodes_dict[next_pos_name]
            actions[agent.name] = {'move': next_pos}
        return actions

    def get_info(self):
        info = {}
        return info


def main():
    set_seed(random_seed_bool=False, i_seed=191)
    # set_seed(random_seed_bool=True)
    alg = RandomMstAlg()
    test_mst_alg(
        alg,
        n_agents=1,
        n_targets=5,
        to_render=True,
        plot_every=1,
        max_steps=520,
    )


if __name__ == '__main__':
    main()
