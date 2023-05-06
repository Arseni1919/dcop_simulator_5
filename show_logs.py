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
               f"A-{logs_info['n_agents']}_T-{logs_info['n_targets']}.json"

    # logs_info.update({
    #     algs_tag: {
    #         'name': algs_dict[algs_tag]['alg'].name,
    #         'col': np.zeros((max_steps, n_problems)),
    #         'rcr': np.zeros((max_steps, n_problems))}
    #     for algs_tag in algs_tags
    # })
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
        plot_col_metrics(ax['A'], logs_info)
        plot_rcr_metrics(ax['B'], logs_info)
        plt.show()


def main():
    file_dir = '2023-05-06--22-01_TT-static_MAP-random-32-32-10_P-3_S-10A-10_T-10.json'
    show_results(file_dir, path='logs/')


if __name__ == '__main__':
    main()

