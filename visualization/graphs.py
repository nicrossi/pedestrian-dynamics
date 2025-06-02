import os
import csv


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

graphs_folder = 'graphs'

if not os.path.exists(graphs_folder):
    os.makedirs(graphs_folder)

def parse_output_file(file):
    data = pd.read_csv(file, index_col='time')
    return data


def parse_output_files(output_folder):
    data = {}
    files = os.listdir(output_folder)
    for file in files:
        if file.endswith('.csv'):
            qin, iteration = file.split('_')[1], file.split('_')[2].split('.')[0]
            data[f"{qin}_{iteration}"] = parse_output_file(os.path.join(output_folder, file))
    return data


### Ex: b
def plot_avg_vx_over_qin(data):
    results = {}
    # Uses only the first iteration for each qin

    for d in data.keys():
        qin, iteration = d.split('_')

        if iteration  != "1": 
            continue

        df = data[d]
        df = df.copy()
        df['second'] = df.index.astype(float).astype(int)

        df = df[(df['second'] >= 10) & (df['second'] <= 40)] # 10s to 40s (or max available)

        grouped = df.groupby('second')

        mean_vx_per_sec = grouped['vx'].apply(lambda x: np.abs(x).mean())

        stderr_vx_per_sec = grouped['vx'].apply(lambda x: np.std(np.abs(x)) / np.sqrt(len(x)))

        average_vx = mean_vx_per_sec.mean()
        std_error_vx = stderr_vx_per_sec.mean()

        results[qin] = {
            'average_vx': average_vx,
            'std_error_vx': std_error_vx
        }

    # Plotting
    sorted_qin = sorted(results.keys(), key=int)

    avg_vx_values = [results[qin]['average_vx'] for qin in sorted_qin]
    std_error_vx_values = [results[qin]['std_error_vx'] for qin in sorted_qin]

    plt.errorbar(sorted_qin, avg_vx_values, yerr=std_error_vx_values, fmt='o', capsize=5)
    plt.xlabel('Qin')
    plt.ylabel('|Vx| Promedio')
    plt.tight_layout()
    plt.grid(True)
    plt.show()

    plt.savefig('graphs/avg_vx_over_qin.png')

### Ex: c
def plot_avg_t_vs_qin(data):

    results = {}

    for d in data.keys():
        qin, iteration = d.split('_')
        df = data[d]

        max_time = df.index.max()

        if qin not in results:
            results[qin] = []
        results[qin].append(max_time)

    results_avg = {qin: np.mean(times) for qin, times in results.items()}
    results_df = pd.DataFrame.from_dict(results_avg, orient='index', columns=['avg_max_time'])
    results_df.index.name = 'qin'

    sorted_qin = sorted(results_df.index, key=int)
    avg_time_values = [results_df.loc[qin, 'avg_max_time'] for qin in sorted_qin]

    std_error_time = results_df['avg_max_time'].std() / np.sqrt(len(results_df))
    std_error_time_values = [std_error_time] * len(sorted_qin)

    plt.errorbar(sorted_qin, avg_time_values, yerr=std_error_time_values, fmt='o', capsize=5)
    plt.xlabel('Qin')
    plt.ylabel('Tiempo Máximo Promedio')
    plt.tight_layout()
    plt.grid(True)
    plt.show()

    plt.savefig('graphs/avg_t_vs_qin.png')




        
    

data = parse_output_files('output')
plot_avg_vx_over_qin(data)
plot_avg_t_vs_qin(data)
