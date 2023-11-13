from globals import *
from functions import *
from algs.test_mst_alg import test_mst_alg


class DsaMstAlgAgent:
    def __init__(self, sim_agent, dsa_p):

        # const
        self.sim_agent = sim_agent
        self.dsa_p = dsa_p
        self.name = self.sim_agent.name
        self.nodes = self.sim_agent.nodes
        self.nodes_dict = self.sim_agent.nodes_dict

        # not const
        self.cred = self.sim_agent.cred
        self.sr = self.sim_agent.sr
        self.mr = self.sim_agent.mr

        # self.pos = self.sim_agent.pos
        # self.nei_targets = self.sim_agent.nei_targets
        # self.nei_agents = self.sim_agent.nei_agents

    def get_nei_temp_req_targets(self):
        nei_temp_req_targets = []
        for target in self.sim_agent.nei_targets:
            nei_temp_req_target = {
                'req': target.req,
                'name': target.name,
                'pos': target.pos
            }
            nei_temp_req_target = AttributeDict(nei_temp_req_target)
            for nei_agent in self.sim_agent.nei_agents:
                if distance_nodes(nei_temp_req_target.pos, nei_agent.pos) <= nei_agent.sr:
                    nei_temp_req_target.req = max(0, nei_temp_req_target.req - nei_agent.cred)
            nei_temp_req_targets.append(nei_temp_req_target)
        return nei_temp_req_targets

    def get_move_order(self):
        # targets = [AttributeDict(target) for target in self.nei_targets]
        next_pos_name = random.choice(self.sim_agent.pos.neighbours)
        next_rand_pos = self.nodes_dict[next_pos_name]
        nei_temp_req_targets = self.get_nei_temp_req_targets()
        if len(nei_temp_req_targets) == 0:
            return next_rand_pos

        new_pos = select_pos(self, nei_temp_req_targets, self.nodes, self.nodes_dict)
        if get_dsa_mst_replacement_decision(self, new_pos, nei_temp_req_targets, self.dsa_p):
            return new_pos
        return self.sim_agent.pos
        # return next_rand_pos

    def test_check(self):
        if any([self.cred != self.sim_agent.cred, self.sr != self.sim_agent.sr, self.mr != self.sim_agent.mr]):
            raise RuntimeError()

    def process(self):
        self.test_check()
        next_pos = self.get_move_order()
        return next_pos

    def update_breakdowns(self, next_pos):
        for nei in self.sim_agent.nei_agents:
            # nei current pos
            if self.sim_agent.pos.xy_name == nei.pos.xy_name:
                return 404
        return next_pos


class DsaMstAlg:
    def __init__(self, dsa_p, with_breakdowns):
        self.name = 'DSA_MST'
        if with_breakdowns:
            self.name = 'DSA_MST \n(with breakdowns)'
        self.agents, self.agents_dict = None, None
        self.sim_targets = None
        self.dsa_p = dsa_p
        self.with_breakdowns = with_breakdowns

    def create_entities(self, sim_agents, sim_targets, sim_nodes):
        self.agents, self.agents_dict = [], {}
        self.sim_targets = sim_targets
        for sim_agent in sim_agents:
            new_agent = DsaMstAlgAgent(sim_agent, self.dsa_p)
            self.agents.append(new_agent)
            self.agents_dict[new_agent.name] = new_agent

    def reset(self, sim_agents, sim_targets, sim_nodes):
        self.create_entities(sim_agents, sim_targets, sim_nodes)

    def get_actions(self):
        actions = {}
        for agent in self.agents:
            next_pos = agent.process()
            actions[agent.name] = {'move': next_pos}

        if self.with_breakdowns:
            for agent in self.agents:
                next_pos = actions[agent.name]['move']
                actions[agent.name]['move'] = agent.update_breakdowns(next_pos)
        return actions

    def get_info(self):
        info = {}
        return info


def main():
    # set_seed(random_seed_bool=False, i_seed=191)
    set_seed(random_seed_bool=True)

    alg = DsaMstAlg(dsa_p=0.8, with_breakdowns=True)
    test_mst_alg(
        alg,
        n_agents=10,
        n_targets=5,
        to_render=True,
        plot_every=10,
        max_steps=520,
    )


if __name__ == '__main__':
    main()
