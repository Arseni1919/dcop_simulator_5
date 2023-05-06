import random

from globals import *
from environments.env_functions import *
from plot_functions.plot_functions import *


class SyncDcopMstEnv:
    def __init__(self, max_steps, map_dir, target_type='static', to_render=True, plot_every=1):
        self.name = 'Sync DCOP-MST Env.'
        self.max_steps = max_steps
        self.map_dir = map_dir
        self.target_type = target_type  # or static or dynamic
        self.to_render = to_render
        self.plot_every = plot_every
        self.with_fmr = None
        # create_new_problem
        self.map_np, self.height, self.width, self.nodes, self.nodes_dict = None, None, None, None, None
        self.agents, self.agents_dict = None, None
        self.targets, self.targets_dict = None, None
        # reset
        self.step_count = None
        self.mailbox = None
        # agent
        self.cred = 20
        self.sr = 5
        self.mr = 2
        # target
        self.req = 100
        self.dynamic_targets_rate = 40  # every X steps the targets change their position

        # for rendering
        self.amount_of_messages_list = None
        # self.fig, self.ax = plt.subplots(2, 2, figsize=(12, 8))
        if self.to_render:
            self.fig, self.ax = plt.subplot_mosaic("AAB;AAC;AAD", figsize=(12, 8))

    def create_new_problem(self, path='maps', n_agents=2, n_targets=2):
        self.map_np, (self.height, self.width) = get_np_from_dot_map(self.map_dir, path=path)
        self.nodes, self.nodes_dict = build_graph_from_np(self.map_np, show_map=False)
        self.agents, self.agents_dict = [], {}
        self.targets, self.targets_dict = [], {}
        positions_pool = random.sample(self.nodes, n_agents + n_targets)

        # create agents
        for i in range(n_agents):
            new_pos = positions_pool.pop()
            new_agent = SimAgent(num=i, cred=self.cred, sr=self.sr, mr=self.mr, pos=new_pos, nodes=self.nodes, nodes_dict=self.nodes_dict)
            self.agents.append(new_agent)
            self.agents_dict[new_agent.name] = new_agent
            # print(f'{new_agent.name} - {new_agent.pos.x}-{new_agent.pos.y}')
            # print(len(positions_pool))

        # create targets
        for i in range(n_targets):
            new_pos = positions_pool.pop()
            new_target = SimTarget(num=i, pos=new_pos, req=self.req, life_start=0, life_end=self.max_steps)
            self.targets.append(new_target)
            self.targets_dict[new_target.name] = new_target
            # print(f'{new_target.name} - {new_target.pos.x}-{new_target.pos.y}')
            # print(len(positions_pool))

    def reset(self, with_fmr=False):

        # reset agents
        _ = [agent.reset() for agent in self.agents]
        self.update_nei_agents()

        # reset targets
        self.with_fmr = with_fmr
        _ = [target.reset() for target in self.targets]
        self.update_rem_cov_req()
        self.update_nei_targets()

        # step count
        self.step_count = 0

        # mailbox
        self.mailbox = {
            agent.name: {i: [] for i in range(self.max_steps)}
            for agent in self.agents
        }
        self.mailbox.update({
            node.xy_name: {i: [] for i in range(self.max_steps)}
            for node in self.nodes
        })

        # for rendering
        self.amount_of_messages_list = []

    def update_dynamic_targets(self):
        n_targets = len(self.targets)
        positions_pool = random.sample(self.nodes, n_targets)
        # update targets
        for target in self.targets:
            new_pos = positions_pool.pop()
            target.pos = new_pos

    def execute_move_order(self, agent, next_pos):
        # --- broken ---
        if agent.is_broken:
            return False

        # --- if not moving and not broken... ---
        if next_pos is None:
            raise RuntimeError('next_pos is None')

        # get broken
        if next_pos == 404:
            agent.get_broken(agent.pos, self.step_count)

        # --- arrived ---
        agent.go_to_next_pos(next_pos)

    def update_rem_cov_req(self):
        for target in self.targets:
            rem_req = target.req
            for agent in self.agents:
                if distance_nodes(target.pos, agent.pos) <= agent.sr:
                    rem_req = max(0, rem_req - agent.cred)
            target.temp_req = rem_req

    def update_fmr_nei(self):
        if self.with_fmr:
            for target in self.targets:
                target.fmr_nei = select_FMR_nei(target, self.targets, self.agents, self.nodes_dict)

    def update_collisions(self):
        _ = [agent.clear_col_agents_list() for agent in self.agents]
        for agent_1, agent_2 in combinations(self.agents, 2):
            if agent_1.pos.xy_name == agent_2.pos.xy_name:
                agent_1.col_agents_list.append(agent_2.name)
                agent_2.col_agents_list.append(agent_1.name)

    def update_nei_targets(self):
        for agent in self.agents:
            nei_targets = []
            for target in self.targets:
                if distance_nodes(agent.pos, target.pos) <= agent.sr + agent.mr:
                    nei_targets.append(target)
            agent.nei_targets = nei_targets

    def update_nei_agents(self):
        logging.debug(f"[ENV]: get_nei_agents")
        for agent in self.agents:
            nei_agents = []
            for other_agent in self.agents:
                if agent.name != other_agent.name:
                    if distance_nodes(agent.pos, other_agent.pos) <= agent.sr + agent.mr + other_agent.sr + other_agent.mr:
                        nei_agents.append(other_agent)
            agent.nei_agents = nei_agents

    def step(self, actions):
        """
        ACTION:
            MOVE ORDER: -1 - wait, 0 - stay, 1 - up, 2 - right, 3 - down, 4 - left
            SEND ORDER: message -> [(from, to, s_time, content), ...]
        """
        logging.debug('[ENV] execute step..')
        # move agents + send agents' messages
        logging.debug("[ENV] move agents + send agents' messages..")
        for agent in self.agents:
            next_pos = actions[agent.name]['move']
            # send_order = actions[agent.name]['send']
            self.execute_move_order(agent, next_pos)
            # self.execute_send_order(send_order)

        # update targets' data
        if self.target_type == 'dynamic':
            if self.step_count % self.dynamic_targets_rate == 0:
                self.update_dynamic_targets()
        self.update_rem_cov_req()
        self.update_fmr_nei()

        # update agents' data
        self.update_collisions()
        self.update_nei_targets()
        self.update_nei_agents()

        # for rendering
        # self.amount_of_messages_list.append(self.calc_amount_of_messages())

        self.step_count += 1

    def render(self, info):
        if self.to_render:
            info = AttributeDict(info)
            if info.i_step % self.plot_every == 0 or info.i_step == self.max_steps - 1:
                info.update({
                    'width': self.width,
                    'height': self.height,
                    'nodes': self.nodes,
                    'targets': self.targets,
                    'agents': self.agents,
                    'aom': self.amount_of_messages_list,
                })

                plot_mst_field(self.ax['A'], info)

                if 'big_experiments' in info:
                    plot_col_metrics(self.ax['B'], info)
                    plot_rcr_metrics(self.ax['C'], info)
                else:
                    if 'col' in info:
                        plot_collisions(self.ax['B'], info)

                    if 'cov' in info:
                        plot_rem_cov_req(self.ax['C'], info)

                    plot_aom(self.ax['D'], info)

                plt.pause(0.001)
                # plt.show()

    def close(self):
        pass

    def sample_actions(self):
        actions = {}
        for agent in self.agents:
            next_pos_name = random.choice(agent.pos.neighbours)
            next_pos = self.nodes_dict[next_pos_name]
            actions[agent.name] = {'move': next_pos}
        return actions


def main():
    max_steps = 120
    # max_steps = 520
    n_problems = 3
    plot_every = 1
    # plot_every = 10

    # map_dir = 'empty-48-48.map'  # 48-48
    map_dir = 'random-64-64-10.map'  # 64-64
    # map_dir = 'warehouse-10-20-10-2-1.map'  # 63-161
    # map_dir = 'lt_gallowstemplar_n.map'  # 180-251

    n_agents = 10
    n_targets = 10
    target_type = 'dynamic'
    # target_type = 'static'

    env = SyncDcopMstEnv(
        max_steps=max_steps,
        map_dir=map_dir,
        target_type=target_type,
        plot_every=plot_every,
    )

    info = {
        'plot_every': env.plot_every,
        'i_alg': env.name,
        'max_steps': env.max_steps
    }

    for i_problem in range(n_problems):
        env.create_new_problem(path='../maps', n_agents=n_agents, n_targets=n_targets)

        # loop on algs

        env.reset(with_fmr=False)

        for i_step in range(env.max_steps):
            # alg - calc actions
            actions = env.sample_actions()

            # env - make a step
            env.step(actions)

            # stats
            pass

            # render
            info['i_problem'] = i_problem
            info['i_step'] = i_step
            env.render(info)


if __name__ == '__main__':
    main()
