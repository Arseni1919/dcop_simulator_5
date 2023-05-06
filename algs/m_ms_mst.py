from globals import *
from functions import *
from algs.test_mst_alg import test_mst_alg


class MaxSumMstAlgAgent:
    def __init__(self, sim_agent, with_breakdowns):
        # const
        self.sim_agent = sim_agent
        self.name = self.sim_agent.name
        self.nodes = self.sim_agent.nodes
        self.nodes_dict = self.sim_agent.nodes_dict

        # not const
        self.cred = self.sim_agent.cred
        self.sr = self.sim_agent.sr
        self.mr = self.sim_agent.mr

        # for MS
        self.beliefs = {}
        self.with_breakdowns = with_breakdowns
        self.next_possible_pos = None
        self.next_possible_pos_list = None

    def exchange_current_pos(self, alg_agents_dict):
        for sim_nei_agent in self.sim_agent.nei_agents:
            alg_nei_agent = alg_agents_dict[sim_nei_agent.name]
            alg_nei_agent.beliefs[self.name] = {
                'pos': self.sim_agent.pos,
            }

    def update_breakdowns(self):
        for nei in self.sim_agent.nei_agents:
            nei_pos = self.beliefs[nei.name]['pos']
            # nei current pos
            if self.sim_agent.pos.xy_name == nei_pos.xy_name:
                self.next_possible_pos = 404
                return

    def decide_ms_next_pos(self):
        if self.next_possible_pos != 404:
            next_pos_name_value_dict = {}
            for next_pos_name in self.sim_agent.pos.neighbours:
                next_pos = self.nodes_dict[next_pos_name]
                next_value = 0
                for target in self.sim_agent.nei_targets:
                    fmr_nei_names = [nei.name for nei in target.fmr_nei]
                    if distance_nodes(next_pos, target.pos) <= self.sr:
                        if self.name in fmr_nei_names:
                            next_value += self.cred
                next_pos_name_value_dict[next_pos_name] = next_value
            max_value = max(next_pos_name_value_dict.values())
            max_pos_names = [k for k, v in next_pos_name_value_dict.items() if v == max_value]
            self.next_possible_pos = self.nodes_dict[random.choice(max_pos_names)]
        self.beliefs = {}


class MaxSumMstAlg:
    def __init__(self, with_breakdowns, max_iters=-1):
        self.name = 'Max-Sum'
        if with_breakdowns:
            self.name = 'Max-Sum (with breakdowns)'
        self.agents, self.agents_dict = None, None
        self.sim_agents, self.sim_targets = None, None
        self.with_breakdowns = with_breakdowns
        self.max_iters = max_iters

    def create_entities(self, sim_agents, sim_targets, sim_nodes):
        self.agents, self.agents_dict = [], {}
        self.sim_targets = sim_targets
        for sim_agent in sim_agents:
            new_agent = MaxSumMstAlgAgent(sim_agent, self.with_breakdowns)
            self.agents.append(new_agent)
            self.agents_dict[new_agent.name] = new_agent

    def reset(self, sim_agents, sim_targets, sim_nodes):
        self.create_entities(sim_agents, sim_targets, sim_nodes)

    def get_actions(self):
        actions = {}

        # exchange
        for agent in self.agents:
            agent.exchange_current_pos(self.agents_dict)

        if self.with_breakdowns:
            for agent in self.agents:
                agent.update_breakdowns()

        # update the next_possible_pos_list + decide next_possible_pos
        for agent in self.agents:
            agent.decide_ms_next_pos()

        # final next_pos
        for agent in self.agents:
            actions[agent.name] = {'move': agent.next_possible_pos}

        return actions

    def get_info(self):
        info = {}
        return info


def main():
    # set_seed(random_seed_bool=False, i_seed=191)
    set_seed(random_seed_bool=True)

    # alg = MaxSumMstAlg(with_breakdowns=False)
    alg = MaxSumMstAlg(with_breakdowns=True)

    test_mst_alg(
        alg,
        n_agents=20,
        n_targets=10,
        to_render=True,
        plot_every=10,
        max_steps=520,
        with_fmr=True,
    )


if __name__ == '__main__':
    main()
