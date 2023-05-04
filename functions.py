from globals import *


def set_seed(random_seed_bool, i_seed=1):
    if random_seed_bool:
        seed = random.randint(0, 1000)
    else:
        seed = i_seed
    random.seed(seed)
    np.random.seed(seed)
    print(f'[SEED]: --- {seed} ---')


def calc_rem_cov_req(targets):
    return sum([target.temp_req for target in targets])


def calc_collisions(agents, step_count):
    collisions = 0
    for agent_1, agent_2 in combinations(agents, 2):
        if agent_1.is_broken and agent_1.broken_time != step_count - 1:
            continue
        if agent_2.is_broken and agent_2.broken_time != step_count - 1:
            continue
        if agent_1.pos.xy_name == agent_2.pos.xy_name:
            collisions += 1
    return collisions
