import numpy as np

from globals import *


font = {
    # 'family': 'serif',
    # 'color':  'darkred',
    'weight': 'normal',
    'size': 22,
}

def plot_rewards(ax, info):
    ax.cla()
    real_rewards = info['real_rewards']
    obs_rewards = info['obs_rewards']
    # real_rewards_before_action = info['real_rewards_before_action']

    max_steps = info['max_steps']
    ax.plot(real_rewards, label='real_rewards')
    ax.plot(obs_rewards, label='obs_rewards')
    # ax.plot(real_rewards_before_action, label='real_rewards_before_action')
    ax.set_xlim(0, max_steps)
    ax.set_title('Rewards')
    ax.legend()


def plot_algs_rewards(ax, info):
    ax.cla()
    max_steps = info['max_steps']
    for alg in info['algs']:
        ax.plot(info['rewards'][alg], label=f'{alg}')

    ax.set_xlim(0, max_steps)
    ax.set_title('Rewards')
    ax.legend()


def plot_mst_field(ax, info):
    ax.cla()
    info = AttributeDict(info)
    # field_np = np.zeros((self.height, self.width))
    field_np = np.zeros((info.width, info.height))
    # add map
    nodes_x, nodes_y = [], []
    for node in info.nodes:
        # field_np[node.x, node.y] = 1
        field_np[node.y, node.x] = 1
        nodes_x.append(node.x)
        nodes_y.append(node.y)

    ax.imshow(field_np, origin='lower', cmap='gray')
    # self.ax['A'].scatter(nodes_x, nodes_y, marker='s', s=14, color='k')
    # self.ax['A'].scatter(nodes_y, nodes_x, marker='s', s=14, color='k')

    # add targets
    targets_x, targets_y = [], []
    for target in info.targets:
        targets_x.append(target.pos.x)
        targets_y.append(target.pos.y)
    ax.scatter(targets_x, targets_y, marker='s', s=14, color='red')
    # self.ax['A'].scatter(targets_y, targets_x, marker='s', s=14, color='red')

    # add agents
    agents_x, agents_y, agents_area = [], [], []
    for agent in info.agents:
        agents_x.append(agent.pos.x)
        agents_y.append(agent.pos.y)
        agents_area.append(agent.sr)
        circle1 = plt.Circle((agent.pos.x, agent.pos.y), agent.sr, color='blue', alpha=0.1)
        # circle1 = plt.Circle((agent.pos.y, agent.pos.x), agent.sr, color='blue', alpha=0.2)
        ax.add_patch(circle1)
    ax.scatter(agents_x, agents_y, marker='o', s=14, color='blue')
    # self.ax['A'].scatter(agents_y, agents_x, marker='o', s=14, color='blue')

    # self.ax['A'].scatter(agents_y, agents_x, marker='o', s=agents_area, color='blue', alpha=0.2)

    ax.set_ylim(0, info.width)
    ax.set_xlim(0, info.height)
    ax.set_title(f'{info.i_alg} | problem: {info.i_problem + 1}, iter: {info.i_step}')


def plot_collisions(ax, info):
    ax.cla()
    info = AttributeDict(info)

    ax.plot(np.cumsum(info.col))
    ax.set_xlim(0, info.max_steps)
    ax.set_title('collisions')


def plot_h_if_all_converged_list(ax, info):
    ax.cla()
    info = AttributeDict(info)

    h_if_all_converged_list = info.h_if_all_converged_list
    ax.plot(h_if_all_converged_list)

    ax.set_title('static_m_percentage')



def plot_static_m_bool_dict(ax, info):
    static_m_bool_dict = info['static_m_bool_dict']
    max_iters = info['max_iters']
    x_list = list(range(max_iters))
    y_list = []
    for i in x_list:
        values = static_m_bool_dict[i]
        y_list.append(np.sum(values)/len(values))
    ax.plot(x_list, y_list)
    ax.set_xlim(0, max_iters)
    ax.set_title('static_m_percentage')


def plot_rem_cov_req(ax, info):
    ax.cla()
    info = AttributeDict(info)

    ax.plot(info.cov)
    ax.set_xlim(0, info.max_steps)
    ax.set_title('Remained Coverage Req.')


def plot_col_metrics(ax, info,with_legend=True):
    ax.cla()
    info = AttributeDict(info)

    for alg_tag in info.algs_tags:
        alg_name = info[alg_tag]['name']
        col_data = info[alg_tag]['col']
        col_data = np.cumsum(col_data, 0)
        col_data = np.mean(col_data, 1)

        ax.plot(col_data, label=f'{alg_name}')
    if with_legend:
        ax.legend(fontsize="14", frameon=False)
    ax.set_xlim(0, info.max_steps)
    ax.set_xlabel('steps\n\n(b)', fontdict=font)
    # ax.set_title('collisions')
    ax.set_ylabel('Collisions', fontdict=font)


def plot_rcr_metrics(ax, info, with_legend=True):
    ax.cla()
    info = AttributeDict(info)

    for alg_tag in info.algs_tags:
        alg_name = info[alg_tag]['name']
        rcr_data = info[alg_tag]['rcr']
        rcr_data = np.mean(rcr_data, 1)

        ax.plot(rcr_data, label=f'{alg_name}')
    if with_legend:
        ax.legend()
    ax.set_xlim(0, info.max_steps)
    ax.set_xlabel('steps\n\n(a)', fontdict=font)
    # ax.set_title('Remained Coverage Req.')
    ax.set_ylabel('Remained Coverage Req.', fontdict=font)


def plot_aom(ax, info):
    # Amount of messages

    ax.cla()
    info = AttributeDict(info)

    ax.plot(info.aom)
    ax.set_xlim(0, info.max_steps)
    ax.set_title('Amount of messages')


