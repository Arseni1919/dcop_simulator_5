from globals import *
from functions import *
from environments.sync_dcop_mst_env import SyncDcopMstEnv
from plot_functions.plot_functions import *
from algs.m_random_mst import RandomMstAlg
from algs.m_dsa_mst import DsaMstAlg
from algs.m_cadsa_mst import CaDsaMstAlg
from algs.m_dssa import DssaAlg
from algs.m_ms_mst import MaxSumMstAlg
from algs.m_cams import CamsAlg
from save_and_show_logs_functions import *


def main():
    # set_seed(random_seed_bool=False, i_seed=597)
    set_seed(random_seed_bool=True)

    n_agents = 20  # !!!
    n_targets = 10  # !!!
    n_problems = 20  # !!!
    # n_problems = 3
    max_steps = 200  # !!!
    # max_steps = 10
    target_type = 'static'
    # target_type = 'dynamic'

    # for render
    # to_render = True
    to_render = False
    plot_every = 50
    # fig, ax = plt.subplot_mosaic("AAB;AAC;AAD", figsize=(12, 8))

    to_save = True
    # to_save = False
    # if n_agents == 50 and n_targets == 20 and n_problems == 20 and max_steps == 200:
    #     to_save = True
    # else:
    #     to_save = False

    # map_dir = 'random-64-64-10.map'  # 64-64

    map_dir = 'random-32-32-10.map'  # 32-32
    # map_dir = 'empty-48-48.map'  # 48-48
    # map_dir = 'warehouse-10-20-10-2-1.map'  # 63-161
    # map_dir = 'lt_gallowstemplar_n.map'  # 180-251

    env = SyncDcopMstEnv(
        max_steps=max_steps,
        map_dir=map_dir,
        target_type=target_type,
        to_render=to_render,
        plot_every=plot_every,
    )
    algs_dict = [
        ('random', {
                'alg': RandomMstAlg(),
                'fmr': False,
                'color': 'blue',
            }),
        ('dsa_mst', {
            'alg': DsaMstAlg(dsa_p=0.8, with_breakdowns=False),
            'fmr': False,
            'color': 'orange',
        }),
        ('dsa_mst-breakdowns', {
                'alg': DsaMstAlg(dsa_p=0.8, with_breakdowns=True),
                'fmr': False,
                'color': 'tab:olive',
            }),
        ('cadsa', {
                'alg': CaDsaMstAlg(dsa_p=0.8),
                'fmr': False,
                'color': 'green',
            }),
        ('dssa', {
            'alg': DssaAlg(dsa_p=0.8),
            'fmr': False,
            'color': 'red',
        }),
        ('ms', {
                'alg': MaxSumMstAlg(with_breakdowns=False),
                'fmr': True,
                'color': 'purple',
            }),
        ('ms-breakdowns', {
                'alg': MaxSumMstAlg(with_breakdowns=True),
                'fmr': True,
                'color': 'brown',
            }),
        ('CAMS', {
            'alg': CamsAlg(with_breakdowns=True, max_iters=10, target_type='BUA'),  # max_iters=20
            'fmr': True,
            'color': 'pink',
        }),
        # ('CAMS (BUA)', {
        #     'alg': CamsAlg(with_breakdowns=True, max_iters=10, target_type='BUA'),  # max_iters=20
        #     'fmr': True,
        #     'color': 'pink',
        #     }),
        # ('CAMS (OVP)', {
        #     'alg': CamsAlg(with_breakdowns=True, max_iters=10, target_type='OVP'),  # max_iters=20
        #     'fmr': True,
        #     'color': 'gray',
        # }),
    ]
    algs_dict = OrderedDict(algs_dict)

    algs_tags = list(algs_dict.keys())

    logs_info = {
        'big_experiments': True,
        'algs_tags': algs_tags,
        'plot_every': env.plot_every,
        'max_steps': env.max_steps,
        'n_agents': n_agents,
        'n_targets': n_targets,
        'n_problems': n_problems,
        'target_type': target_type,
        'map_dir': map_dir,
    }
    logs_info.update({
        algs_tag: {
            # 'name': algs_dict[algs_tag]['alg'].name,
            'name': algs_dict[algs_tag]['alg'].name,
            'col': np.zeros((max_steps, n_problems)),
            'rcr': np.zeros((max_steps, n_problems)),
            'color': algs_dict[algs_tag]['color'],
        }
        for algs_tag in algs_tags
    })

    for i_problem in range(n_problems):
        env.create_new_problem(path='maps', n_agents=n_agents, n_targets=n_targets)
        print()

        for alg_tag in algs_tags:
            alg = algs_dict[alg_tag]['alg']
            with_fmr = algs_dict[alg_tag]['fmr']
            # environment reset
            env.reset(with_fmr=with_fmr)
            # algorithm reset
            alg.reset(env.agents, env.targets, env.nodes)

            for i_step in range(env.max_steps):

                # alg - calc actions
                actions = alg.get_actions()

                # env - make a step
                env.step(actions)

                # stats
                pass

                # logs
                logs_info['i_problem'] = i_problem
                logs_info['i_alg'] = alg_tag
                logs_info['i_step'] = i_step
                logs_info[alg_tag]['col'][i_step, i_problem] = calc_collisions(env.agents, env.step_count)
                logs_info[alg_tag]['rcr'][i_step, i_problem] = calc_rem_cov_req(env.targets)

                # render
                print(f'\r[big experiments]: tt={target_type}, {map_dir}, {i_problem=}, {alg.name=}, {i_step=}', end='')

                # from alg
                # alg_info = alg.get_info()
                env.render(logs_info)
                plt.pause(0.001)

    # save data
    if to_save:
        file_dir = save_results(logs_info)
        show_results(file_dir)

    plt.show()
    env.close()


if __name__ == '__main__':
    # profiler = None
    profiler = cProfile.Profile()
    if profiler:
        profiler.enable()
    main()
    if profiler:
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumtime')
        stats.dump_stats('stats/results_scale_experiments.pstat')
        print('\nProfile saved to stats/results_scale_experiments.pstat.')
        # in terminal: snakeviz stats/results_scale_experiments.pstat
