from globals import *


def set_seed(random_seed_bool, i_seed=1):
    if random_seed_bool:
        seed = random.randint(0, 1000)
    else:
        seed = i_seed
    random.seed(seed)
    np.random.seed(seed)
    print(f'[SEED]: --- {seed} ---')


def check_if_all_agents_converged(agents, max_iters):
    all_agents_converged_list = []
    for agent in agents:
        last_iter_bool = agent.static_m_bool_dict[max_iters - 1][-1]
        all_agents_converged_list.append(last_iter_bool)
    return all(all_agents_converged_list)


def check_if_last_n_messages_the_same(h_messages_dict, n):
    # self.h_messages_dict[pos_name].append(value)
    output_list = []
    for _, m_values in h_messages_dict.items():
        output_list.append(len(m_values) >= n and len(set(m_values[-n:])) == 1)
    return all(output_list)


def calc_rem_cov_req(targets):
    return sum([target.temp_req for target in targets])


def calc_collisions(agents, step_count):
    collisions = 0
    for agent in agents:
        if agent.is_broken:
            continue
        for other_agent in agents:
            if agent.name != other_agent.name:
                if agent.pos.xy_name == other_agent.pos.xy_name:
                    collisions += 1
                    break
    return collisions


def distance_nodes(node1, node2):
    return np.sqrt((node1.x - node2.x) ** 2 + (node1.y - node2.y) ** 2)


def distance(pos1, pos2):
    return math.sqrt(math.pow(pos1[0] - pos2[0], 2) + math.pow(pos1[1] - pos2[1], 2))


def within_sr_from_most(robot, robot_pos_name_set, target_set, pos_dict_name_pos):
    within_sr_range_dict = {}
    max_list = []
    for robot_name in robot_pos_name_set:
        count = sum([distance(target.pos.xy_pos, pos_dict_name_pos[robot_name]) < robot.sr for target in target_set])
        max_list.append(count)
        within_sr_range_dict[robot_name] = count
    max_value = max(max_list)

    within_sr_range_list, target_set_to_send = [], []
    for robot_name, count in within_sr_range_dict.items():
        if count == max_value:
            within_sr_range_list.append(robot_name)
            target_set_to_send.extend(list(filter(
                lambda x: distance(x.pos.xy_pos, pos_dict_name_pos[robot_name]) < robot.sr,
                target_set
            )))
    target_set_names_dict = {t.name: t for t in target_set_to_send}
    target_set_to_send = list(target_set_names_dict.values())
    # target_set_to_send = list(set(target_set_to_send))
    return within_sr_range_list, target_set_to_send


def select_pos_internal(robot, robot_pos_name_set, funcs, pos_dict_name_pos):
    max_func_value = max([target.req for target in funcs]) if len(funcs) > 0 else 0
    if len(robot_pos_name_set) == 1 or max_func_value < 1:
        return random.sample(robot_pos_name_set, 1)[0]
    target_set = []
    for target in funcs:
        if target.req == max_func_value:
            if any([distance(target.pos.xy_pos, pos_dict_name_pos[p_n]) < robot.sr for p_n in robot_pos_name_set]):
                target_set.append(target)

    if len(target_set) == 0:
        return random.sample(robot_pos_name_set, 1)[0]

    within_sr_range_list, target_set = within_sr_from_most(robot, robot_pos_name_set, target_set, pos_dict_name_pos)
    for target in target_set:
        funcs.remove(target)

    return select_pos_internal(robot, within_sr_range_list, funcs, pos_dict_name_pos)


def select_pos(robot, targets, nodes, nodes_dict, next_possible_pos_list=None):
    if next_possible_pos_list is None:
        robot_pos_name_set = [pos_name for pos_name in robot.sim_agent.pos.neighbours]
    else:
        robot_pos_name_set = [pos_node.xy_name for pos_node in next_possible_pos_list]
    pos_dict_name_pos = {pos_node.xy_name: pos_node.xy_pos for pos_node in nodes}
    next_pos_name = select_pos_internal(robot, robot_pos_name_set, targets, pos_dict_name_pos)
    return nodes_dict[next_pos_name]


def get_dsa_mst_replacement_decision(agent, new_pos, nei_targets, dsa_p):
    old_value, new_value = 0, 0
    for target in nei_targets:
        # update old_value
        if distance_nodes(target.pos, agent.sim_agent.pos) <= agent.sr:
            old_value += min(target.req, agent.sr)
        # update new value
        if distance_nodes(target.pos, new_pos) <= agent.sr:
            new_value += min(target.req, agent.sr)
    # compare
    if new_value >= old_value:
        # random return
        return random.random() < dsa_p
    return False

