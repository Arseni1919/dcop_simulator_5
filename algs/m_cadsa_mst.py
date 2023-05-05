from globals import *
from functions import *
from algs.test_mst_alg import test_mst_alg


class CaDsaMstAlgAgent:
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

        self.next_possible_pos = None
        self.beliefs = {}

        # states
        """
        first
        v
        exchange -> plan -> ca_correction -> move
        ^                                       v                                                    v
        <-<-<-<-<-<-<-<-<--<-<-<-<-<-<-<-<-<-<-<-
        """

    def next_pos_without_collisions(self):
        # if there is a possible collision -> stay on place
        for nei in self.sim_agent.nei_agents:
            nei_next_possible_pos = self.beliefs[nei.name]['next_possible_pos']
            nei_pos = self.beliefs[nei.name]['pos']
            if nei_next_possible_pos is None:
                raise RuntimeError()
            if self.next_possible_pos.xy_name == nei_next_possible_pos.xy_name:
                return self.sim_agent.pos
            if self.next_possible_pos.xy_name == nei_pos.xy_name:
                return self.sim_agent.pos
        return self.next_possible_pos

    def test_check(self):
        if any([self.cred != self.sim_agent.cred, self.sr != self.sim_agent.sr, self.mr != self.sim_agent.mr]):
            raise RuntimeError()

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

    def decide_next_possible_pos(self):
        self.next_possible_pos = self.get_move_order()
        self.beliefs = {}

    def exchange_next_possible_pos(self, alg_agents_dict):
        for sim_nei_agent in self.sim_agent.nei_agents:
            alg_nei_agent = alg_agents_dict[sim_nei_agent.name]
            alg_nei_agent.beliefs[self.name] = {
                'pos': self.sim_agent.pos,
                'next_possible_pos': self.next_possible_pos
            }

    def decide_next_final_pos(self):
        self.test_check()
        next_pos = self.next_pos_without_collisions()
        return next_pos


class CaDsaMstAlg:
    def __init__(self, dsa_p):
        self.name = 'CADSA'
        self.agents, self.agents_dict = None, None
        self.sim_targets = None
        self.dsa_p = dsa_p

    def create_entities(self, sim_agents, sim_targets, sim_nodes):
        self.agents, self.agents_dict = [], {}
        self.sim_targets = sim_targets
        for sim_agent in sim_agents:
            new_agent = CaDsaMstAlgAgent(sim_agent, self.dsa_p)
            self.agents.append(new_agent)
            self.agents_dict[new_agent.name] = new_agent

    def reset(self, sim_agents, sim_targets, sim_nodes):
        self.create_entities(sim_agents, sim_targets, sim_nodes)

    def get_actions(self):
        actions = {}

        # decide next move
        for agent in self.agents:
            agent.decide_next_possible_pos()

        # exchange
        for agent in self.agents:
            agent.exchange_next_possible_pos(self.agents_dict)

        # collision avoidance
        for agent in self.agents:
            next_pos = agent.decide_next_final_pos()
            actions[agent.name] = {'move': next_pos}
        return actions

    def get_info(self):
        info = {}
        return info


def main():
    set_seed(random_seed_bool=False, i_seed=191)
    # set_seed(random_seed_bool=True)
    alg = CaDsaMstAlg(dsa_p=0.8)
    # test_mst_alg(alg, to_render=False)
    # test_mst_alg(alg, to_render=True, plot_every=10)
    # set_seed(True, 353)
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
