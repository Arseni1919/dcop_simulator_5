from globals import *
from functions import *
from algs.test_mst_alg import test_mst_alg


class DssaAlgAgent:
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

        # for DSSA
        self.beliefs = {}
        self.next_possible_pos = None
        self.next_possible_pos_list = None

    # def reset_beliefs(self):
    #     self.beliefs = {}
    #     for agent in self.all_agents:
    #         # create belief if this is new agent
    #         self.beliefs[agent['name']] = {
    #             'next_possible_pos': None,
    #             'state': '',
    #             'tries': None,
    #             'need_to_talk': False,
    #         }

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
        if len(self.next_possible_pos_list) == 0:
            return self.sim_agent.pos
        next_rand_pos = random.choice(self.next_possible_pos_list)
        nei_temp_req_targets = self.get_nei_temp_req_targets()
        if len(nei_temp_req_targets) == 0:
            return next_rand_pos

        new_pos = select_pos(self, nei_temp_req_targets, self.nodes, self.nodes_dict, self.next_possible_pos_list)
        if get_dsa_mst_replacement_decision(self, new_pos, nei_temp_req_targets, self.dsa_p):
            return new_pos
        return self.sim_agent.pos

    def first_decide_next_possible_pos(self):
        self.next_possible_pos_list = [self.nodes_dict[node_name] for node_name in self.sim_agent.pos.neighbours]
        self.next_possible_pos = self.get_move_order()
        self.beliefs = {}

    def update_next_possible_pos(self):
        if self.there_is_a_collision():
            if self.next_possible_pos in self.next_possible_pos_list:
                self.next_possible_pos_list.remove(self.next_possible_pos)
            self.next_possible_pos = self.get_move_order()
        self.beliefs = {}

    def exchange_next_possible_pos(self, alg_agents_dict):
        for sim_nei_agent in self.sim_agent.nei_agents:
            alg_nei_agent = alg_agents_dict[sim_nei_agent.name]
            alg_nei_agent.beliefs[self.name] = {
                'pos': self.sim_agent.pos,
                'next_possible_pos': self.next_possible_pos
            }

    def there_is_a_collision(self):
        # if there is a possible collision -> stay on place
        for nei in self.sim_agent.nei_agents:
            nei_next_possible_pos = self.beliefs[nei.name]['next_possible_pos']
            nei_pos = self.beliefs[nei.name]['pos']
            if nei_next_possible_pos is None:
                raise RuntimeError()
            # nei next pos
            if self.next_possible_pos.xy_name == nei_next_possible_pos.xy_name:
                return True
            # nei current pos
            if self.next_possible_pos.xy_name == nei_pos.xy_name:
                return True
        return False

    # def there_is_a_collision(self):
    #     # if there is a possible collision -> stay on place
    #     for nei in self.nei_agents:
    #         nei_name = nei['name']
    #         nei_pos = nei['pos']
    #         nei_next_possible_pos = self.beliefs[nei_name]['next_possible_pos']
    #         # nei_need_to_talk = self.beliefs[nei_name]['need_to_talk']
    #         # if nei_need_to_talk:
    #         #     return True
    #         if nei_next_possible_pos is None:
    #             raise RuntimeError()
    #         if self.next_possible_pos.xy_name == nei_next_possible_pos.xy_name:
    #             return True
    #         if self.next_possible_pos.xy_name == nei_pos.xy_name:
    #             return True
    #     return False

    # def state_plan(self):
    #     """
    #     DSSA:
    #     Exchange next possible positions until the solution without collisions will be found.
    #     Each time exclude the problematic position.
    #     """
    #     move_order = -1
    #     send_order = self.get_send_order()
    #
    #     self.need_to_talk = self.there_is_a_collision()
    #     # if collision with other agents - we still need to talk
    #     if self.need_to_talk:
    #         self.tries += 1
    #         nei_targets = [AttributeDict(target) for target in self.nei_targets]
    #         if not get_dsa_mst_replacement_decision(self, self.next_possible_pos, nei_targets):
    #             # set different next position
    #             if self.next_possible_pos in self.possible_next_pos_list:
    #                 self.possible_next_pos_list.remove(self.next_possible_pos)
    #             robot_pos_name_set = [pos.xy_name for pos in self.possible_next_pos_list]
    #             self.decide_next_possible_move(robot_pos_name_set=robot_pos_name_set)
    #     if not self.need_to_talk:
    #         self.state = 'f_plan'
    #     if self.tries > self.max_tries:
    #         self.state = 'f_plan'
    #         self.next_possible_pos, self.next_possible_action = self.pos, 0
    #     return move_order, send_order


class DssaAlg:
    def __init__(self, dsa_p):
        self.name = 'DSSA'
        self.agents, self.agents_dict = None, None
        self.sim_targets = None
        self.dsa_p = dsa_p
        self.max_tries = 20

    def create_entities(self, sim_agents, sim_targets, sim_nodes):
        self.agents, self.agents_dict = [], {}
        self.sim_targets = sim_targets
        for sim_agent in sim_agents:
            new_agent = DssaAlgAgent(sim_agent, self.dsa_p)
            self.agents.append(new_agent)
            self.agents_dict[new_agent.name] = new_agent

    def reset(self, sim_agents, sim_targets, sim_nodes):
        self.create_entities(sim_agents, sim_targets, sim_nodes)

    def there_are_collisions(self):
        for agent in self.agents:
            if agent.there_is_a_collision():
                return True
        return False

    def get_actions(self):
        actions = {}

        # first time - decide next move
        for agent in self.agents:
            agent.first_decide_next_possible_pos()

        # first exchange
        for agent in self.agents:
            agent.exchange_next_possible_pos(self.agents_dict)

        tries = 0
        while self.there_are_collisions():
            tries += 1
            # update the next_possible_pos_list + decide next_possible_pos
            for agent in self.agents:
                agent.update_next_possible_pos()

            # exchange
            for agent in self.agents:
                agent.exchange_next_possible_pos(self.agents_dict)

            # if there are too many tries and still a collision -> stay on the same spot
            if tries > self.max_tries:
                for agent in self.agents:
                    if agent.there_is_a_collision():
                        agent.next_possible_pos = agent.sim_agent.pos
                break

        # final next_pos
        for agent in self.agents:
            actions[agent.name] = {'move': agent.next_possible_pos}
        return actions

    def get_info(self):
        info = {}
        return info


def main():
    set_seed(random_seed_bool=False, i_seed=191)
    # set_seed(random_seed_bool=True)

    alg = DssaAlg(dsa_p=0.8)
    test_mst_alg(
        alg,
        n_agents=30,
        n_targets=5,
        to_render=True,
        plot_every=50,
        max_steps=520,
    )


if __name__ == '__main__':
    main()
