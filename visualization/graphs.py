import os
import csv


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

graphs_folder = 'graphs'

if not os.path.exists(graphs_folder):
    os.makedirs(graphs_folder)

def parse_output_file(file):
    # data = {}
    # with open(file, 'r') as f:
    #     reader = csv.DictReader(f)
    #     for row in reader:
    #         time_key = float(row["time"]) 
    #         value = {key: float(val) for key, val in row.items() if key != "time"}
    #         data[time_key] = value
    data = pd.read_csv(file, index_col='time')
    return data


def parse_output_files(output_folder):
    data = {}
    files = os.listdir(output_folder)
    for file in files:
        if file.endswith('.csv'):
            qin = int(file.split('_')[1].split('.')[0])
            data[qin] = parse_output_file(os.path.join(output_folder, file))

    return data


### Ex: b
def plot_avg_vx_over_qin(data):
    results = {}
    for qin in data.keys():
        df = data[qin]
        df = df.copy()
        df['second'] = df.index.astype(float).astype(int)

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
    

data = parse_output_files('output')
print(plot_avg_vx_over_qin(data))

