from globals import *
from environments.sync_dcop_mst_env import SyncDcopMstEnv
from functions import calc_collisions, calc_rem_cov_req


def test_mst_alg(alg,
                 n_agents=20,
                 n_targets=10,
                 target_type='static',
                 max_steps=120,
                 n_problems=3,
                 to_render=True,
                 plot_every=10,
                 with_fmr=False,
                 ):

    map_dir = 'random-32-32-10.map'  # 32-32
    # map_dir = 'empty-48-48.map'  # 48-48
    # map_dir = 'random-64-64-10.map'  # 64-64
    # map_dir = 'warehouse-10-20-10-2-1.map'  # 63-161
    # map_dir = 'lt_gallowstemplar_n.map'  # 180-251

    env = SyncDcopMstEnv(
        max_steps=max_steps,
        map_dir=map_dir,
        target_type=target_type,
        to_render=to_render,
        plot_every=plot_every,
    )
    info = {'plot_every': env.plot_every, 'max_steps': env.max_steps}

    for i_problem in range(n_problems):
        env.create_new_problem(path='../maps', n_agents=n_agents, n_targets=n_targets)

        # <-- loop on algs

        # environment reset
        env.reset(with_fmr=with_fmr)
        # algorithm reset
        alg.reset(env.agents, env.targets, env.nodes)

        # logs
        info['i_alg'] = alg.name
        info['col'] = []
        info['cov'] = []

        for i_step in range(env.max_steps):

            # alg - calc actions
            actions = alg.get_actions()

            # env - make a step
            env.step(actions)

            # stats
            pass

            # logs
            info['i_problem'] = i_problem
            info['i_step'] = i_step
            info['col'].append(calc_collisions(env.agents, env.step_count))
            info['cov'].append(calc_rem_cov_req(env.targets))

            # render
            print(f'\r[test_mst_alg]: alg name= {alg.name}, map name= {map_dir}, {i_problem=}, {i_step=}', end='')
            # from alg
            alg_info = alg.get_info()
            info.update(alg_info)
            env.render(info)

    plt.show()


def main():
    pass


if __name__ == '__main__':
    main()
