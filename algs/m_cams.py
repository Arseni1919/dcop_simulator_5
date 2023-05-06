from globals import *
from functions import *
from algs.test_mst_alg import test_mst_alg


def flatten_message(message, to_flatten=True):
    if to_flatten:
        min_value = min(message.values())
        return {pos_i: value - min_value for pos_i, value in message.items()}
    return message


# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# -------------------------------------------CamsAlgPosNode--------------------------------------------- #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #

class CamsAlgPosNode:
    def __init__(self, pos):
        self.pos = pos
        self.name = pos.xy_name
        self.step_count = None
        self.mailbox = {}
        self.requests_list = []
        self.beliefs = {}

        self.inf_cost = -900000
        self.dust = {}

        self.nei_agents = None

    def update_nei_agents(self, agents):
        self.nei_agents = []
        for other_agent in agents:
            if self.name in other_agent.sim_agent.pos.neighbours:
                self.nei_agents.append(other_agent)

    def update_dust_weights(self, agents):
        self.dust = {}
        for agent in agents:
            self.dust[agent.name] = random.uniform(1e-10, 1e-5)

    def reset_beliefs(self):
        # self.beliefs[other_agent.name][pos_name_2]
        self.beliefs = {
            agent.name: {
                pos_name: 0 for pos_name in agent.sim_agent.pos.neighbours
            }
            for agent in self.nei_agents
        }

    def is_with_nei(self):
        return len(self.nei_agents) > 0

    def calc_belief_for_agent(self, agent):
        agent_domain_names_list = agent.sim_agent.pos.neighbours
        func_message = {pos_name: 0 for pos_name in agent_domain_names_list}
        if len(self.nei_agents) <= 1:
            func_message[self.name] = self.dust[agent.name]
        if len(self.nei_agents) > 2:
            func_message[self.name] = self.inf_cost
        if len(self.nei_agents) == 2:
            nei_agents_copy = self.nei_agents[:]
            nei_agents_copy.remove(agent)
            other_agent = nei_agents_copy[0]
            other_agent_domain_names_agent = other_agent.sim_agent.pos.neighbours
            for pos_name_1 in agent_domain_names_list:
                # row
                row_values = []
                for pos_name_2 in other_agent_domain_names_agent:
                    # column
                    col_value = 0
                    col_value += self.beliefs[other_agent.name][pos_name_2]
                    if pos_name_1 == self.name and pos_name_2 == self.name:
                        col_value = self.inf_cost
                    elif pos_name_1 == self.name:
                        col_value += self.dust[agent.name]
                    elif pos_name_2 == self.name:
                        col_value += self.dust[other_agent.name]

                    row_values.append(col_value)

                func_message[pos_name_1] = max(row_values)

        return func_message

    def send_messages(self):
        for agent in self.nei_agents:
            func_message = self.calc_belief_for_agent(agent)
            agent.beliefs[self.name] = func_message

# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ----------------------------------------------CamsAlgAgent-------------------------------------------- #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #


class CamsAlgAgent:
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
        self.nei_alg_pos_nodes = None
        self.beliefs = {}
        self.with_breakdowns = with_breakdowns
        self.next_possible_pos = None

    def reset_beliefs(self):
        self.beliefs = {}

    def get_nei_alg_pos_nodes(self, alg_pos_nodes_dict):
        self.nei_alg_pos_nodes = []
        for pos_name in self.sim_agent.pos.neighbours:
            alg_pos_node = alg_pos_nodes_dict[pos_name]
            self.nei_alg_pos_nodes.append(alg_pos_node)

    def get_value_from_targets(self, nei_pos):
        nei_pos_value = 0
        for target in self.sim_agent.nei_targets:
            fmr_nei_names = [nei.name for nei in target.fmr_nei]
            if distance_nodes(nei_pos, target.pos) <= self.sr:
                if self.name in fmr_nei_names:
                    nei_pos_value += self.cred
        return nei_pos_value

    def create_ms_message_with_target_upload(self):
        domain_names_list = self.sim_agent.pos.neighbours
        # create new ms message
        ms_message = {nei_pos_name: 0 for nei_pos_name in domain_names_list}
        # add from targets
        for nei_pos_name in domain_names_list:
            nei_pos = self.nodes_dict[nei_pos_name]
            nei_pos_value = self.get_value_from_targets(nei_pos)
            # nei_pos_value = 0
            # for target in self.sim_agent.nei_targets:
            #     fmr_nei_names = [nei.name for nei in target.fmr_nei]
            #     if distance_nodes(nei_pos, target.pos) <= self.sr:
            #         if self.name in fmr_nei_names:
            #             nei_pos_value += self.cred
            ms_message[nei_pos_name] = nei_pos_value
        return ms_message

    def add_others_pos_nodes_upload(self, alg_pos_node, ms_message):
        domain_names_list = self.sim_agent.pos.neighbours
        for other_alg_pos_node in self.nei_alg_pos_nodes:
            if other_alg_pos_node.name != alg_pos_node.name:
                believed_alg_pos_values = self.beliefs[other_alg_pos_node.name]
                for next_pos_name in domain_names_list:
                    ms_message[next_pos_name] += believed_alg_pos_values[next_pos_name]
        return ms_message

    def send_messages(self):
        for nei_alg_pose_node in self.nei_alg_pos_nodes:
            ms_message_with_target_upload = self.create_ms_message_with_target_upload()
            var_message = self.add_others_pos_nodes_upload(nei_alg_pose_node, ms_message_with_target_upload)
            var_message = flatten_message(var_message)
            nei_alg_pose_node.beliefs[self.name] = var_message

    def decide_cams_next_possible_pos(self):
        next_pos_value_dict = {}
        domain_names_list = self.sim_agent.pos.neighbours
        for next_pos_name in domain_names_list:
            next_pos_value = 0
            next_pos = self.nodes_dict[next_pos_name]

            # targets
            next_pos_value += self.get_value_from_targets(next_pos)

            # pos_nodes
            for pos_node_name in domain_names_list:
                pos_node_additional_value = self.beliefs[pos_node_name][next_pos.xy_name]
                next_pos_value += pos_node_additional_value

            next_pos_value_dict[next_pos_name] = next_pos_value

        max_value = max(next_pos_value_dict.values())
        next_possible_pos_name = random.choice([k for k, v in next_pos_value_dict.items() if v == max_value])
        self.next_possible_pos = self.nodes_dict[next_possible_pos_name]

    def exchange_current_pos(self, alg_agents_dict):
        for sim_nei_agent in self.sim_agent.nei_agents:
            alg_nei_agent = alg_agents_dict[sim_nei_agent.name]
            alg_nei_agent.beliefs[self.name] = {
                'pos': self.sim_agent.pos,
                'next_possible_pos': self.next_possible_pos
            }

    def update_breakdowns(self):
        for nei in self.sim_agent.nei_agents:
            nei_pos = self.beliefs[nei.name]['pos']
            # nei current pos
            if self.sim_agent.pos.xy_name == nei_pos.xy_name:
                self.next_possible_pos = 404
                return

    def get_next_pos_without_collisions(self):
        # if there is a possible collision -> stay on place
        for nei in self.sim_agent.nei_agents:
            nei_next_possible_pos = self.beliefs[nei.name]['next_possible_pos']
            nei_pos = self.beliefs[nei.name]['pos']
            if nei_next_possible_pos is None:
                raise RuntimeError()
            # its future pos
            if self.next_possible_pos.xy_name == nei_next_possible_pos.xy_name:
                return self.sim_agent.pos
            # its current pos
            if self.next_possible_pos.xy_name == nei_pos.xy_name:
                return self.sim_agent.pos
        return self.next_possible_pos

    def check_next_pos_without_collisions(self):
        # check
        prev_name = self.next_possible_pos.xy_name
        next_new_pos = self.get_next_pos_without_collisions()
        new_name = next_new_pos.xy_name
        if prev_name != new_name:
            print(f'\nprev_name != new_name -> ({prev_name})-({new_name})')
        # to change
        self.next_possible_pos = next_new_pos


# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# -----------------------------------------------CamsAlg------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #

class CamsAlg:
    def __init__(self, with_breakdowns, max_iters):
        self.name = 'CAMS'
        self.agents, self.agents_dict = None, None
        self.alg_pos_nodes, self.alg_pos_nodes_dict = None, None
        self.sim_agents, self.sim_targets, self.sim_nodes = None, None, None
        self.all_entities, self.all_entities_dict = None, None
        self.with_breakdowns = with_breakdowns
        self.max_iters = max_iters

    def create_entities(self, sim_agents, sim_targets, sim_nodes):
        self.sim_agents, self.sim_targets, self.sim_nodes = sim_agents, sim_targets, sim_nodes
        self.all_entities, self.all_entities_dict = [], {}

        self.agents, self.agents_dict = [], {}
        for sim_agent in sim_agents:
            new_agent = CamsAlgAgent(sim_agent, self.with_breakdowns)
            self.agents.append(new_agent)
            self.agents_dict[new_agent.name] = new_agent
            self.all_entities.append(new_agent)
            self.all_entities_dict[new_agent.name] = new_agent

        self.alg_pos_nodes, self.alg_pos_nodes_dict = [], {}
        for node in sim_nodes:
            new_pos_node = CamsAlgPosNode(node)
            self.alg_pos_nodes.append(new_pos_node)
            self.alg_pos_nodes_dict[new_pos_node.name] = new_pos_node
            self.all_entities.append(new_pos_node)
            self.all_entities_dict[new_pos_node.name] = new_pos_node

    def reset(self, sim_agents, sim_targets, sim_nodes):
        self.create_entities(sim_agents, sim_targets, sim_nodes)

    def get_actions(self):
        actions = {}

        # preparation
        relevant_alg_pos_nodes = []
        for alg_pos_node in self.alg_pos_nodes:
            alg_pos_node.update_nei_agents(self.agents)
            alg_pos_node.update_dust_weights(self.agents)
            alg_pos_node.reset_beliefs()
            if len(alg_pos_node.nei_agents) > 0:
                relevant_alg_pos_nodes.append(alg_pos_node)
        for agent in self.agents:
            agent.get_nei_alg_pos_nodes(self.alg_pos_nodes_dict)
            agent.reset_beliefs()

        # ITERATIONS
        for small_iter in range(self.max_iters):

            # alg_pos_nodes send messages
            for alg_pos_node in relevant_alg_pos_nodes:
                alg_pos_node.send_messages()

            # agents send messages
            for agent in self.agents:
                agent.send_messages()

        # decide next_possible_pos
        for agent in self.agents:
            agent.decide_cams_next_possible_pos()

        # exchange current position
        for agent in self.agents:
            agent.exchange_current_pos(self.agents_dict)

        if self.with_breakdowns:
            for agent in self.agents:
                agent.update_breakdowns()

        # collision avoidance correction/checking
        for agent in self.agents:
            agent.check_next_pos_without_collisions()

        # final next_pos
        for agent in self.agents:
            actions[agent.name] = {'move': agent.next_possible_pos}

        return actions

    def get_info(self):
        info = {}
        return info


def main():
    set_seed(random_seed_bool=False, i_seed=597)
    # set_seed(random_seed_bool=True)

    # alg = CamsAlg(with_breakdowns=False, max_iters=10)
    alg = CamsAlg(with_breakdowns=True, max_iters=10)

    test_mst_alg(
        alg,
        n_agents=40,
        n_targets=10,
        to_render=True,
        # to_render=False,
        plot_every=10,
        max_steps=520,
        with_fmr=True,
    )


if __name__ == '__main__':
    main()
