import matplotlib.pyplot as plt

from globals import *
from functions import *
from plot_functions.plot_functions import *


def save_results(logs_info):
    """
    json.dumps() method can convert a Python object into a JSON string.
    json.dump() method can be used for writing to JSON file.
    """
    file_dir = f"logs/{datetime.now().strftime('%Y-%m-%d--%H-%M')}_" \
               f"TT-{logs_info['target_type']}_" \
               f"MAP-{logs_info['map_dir'][:-4]}___" \
               f"P-{logs_info['n_problems']}_S-{logs_info['max_steps']}___" \
               f"_a10___" \  
               f"A-{logs_info['n_agents']}_T-{logs_info['n_targets']}.json"
    for alg_tag in logs_info['algs_tags']:
        logs_info[alg_tag]['col'] = logs_info[alg_tag]['col'].tolist()
        logs_info[alg_tag]['rcr'] = logs_info[alg_tag]['rcr'].tolist()
    json_object = json.dumps(logs_info, indent=2)
    with open(file_dir, "w") as outfile:
        outfile.write(json_object)

    return file_dir


def show_results(file_dir, path=''):
    with open(f'{path}{file_dir}', 'r') as openfile:
        # Reading from json file
        logs_info = json.load(openfile)
        for alg_tag in logs_info['algs_tags']:
            logs_info[alg_tag]['col'] = np.array(logs_info[alg_tag]['col'])
            logs_info[alg_tag]['rcr'] = np.array(logs_info[alg_tag]['rcr'])
        fig, ax = plt.subplot_mosaic("AB;AB", figsize=(12, 8))
        plot_rcr_metrics(ax['A'], logs_info, with_legend=False)
        plot_col_metrics(ax['B'], logs_info)
        # plot_rcr_metrics(ax['B'], logs_info, with_legend=True)
        # plt.title(f"{logs_info['map_dir'][:-4]} Map")
        fig.suptitle(f"{logs_info['map_dir'][:-4]} Map", fontsize=16)
        plt.tight_layout()
        plt.show()


def main():
    # TT static
    # file_dir = '2023-05-06--22-14_TT-static_MAP-random-32-32-10___P-20_S-200___A-20_T-10.json'
    # file_dir = '2023-05-06--22-23_TT-static_MAP-empty-48-48___P-20_S-200___A-20_T-10.json'
    # file_dir = '2023-05-06--22-31_TT-static_MAP-warehouse-10-20-10-2-1___P-20_S-200___A-20_T-10.json'
    # file_dir = '2023-05-06--22-46_TT-static_MAP-lt_gallowstemplar_n___P-20_S-200___A-20_T-10.json'

    # TT dynamic
    # file_dir = '2023-05-06--23-10_TT-dynamic_MAP-random-32-32-10___P-20_S-200___A-20_T-10.json'
    # file_dir = '2023-05-06--23-16_TT-dynamic_MAP-empty-48-48___P-20_S-200___A-20_T-10.json'
    # file_dir = '2023-05-06--23-23_TT-dynamic_MAP-warehouse-10-20-10-2-1___P-20_S-200___A-20_T-10.json'
    file_dir = '2023-05-06--23-37_TT-dynamic_MAP-lt_gallowstemplar_n___P-20_S-200___A-20_T-10.json'

    # ADDITIONAL EXPERIMENTS
    # 

    show_results(file_dir, path='logs/')


if __name__ == '__main__':
    main()

