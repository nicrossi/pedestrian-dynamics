import os, csv, glob, re
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

graphs_folder = 'graphs'
OUT_DIR = "output"
WINDOW = 1.0
T1, T2 = 10.0, 40.0

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
    plt.savefig('graphs/avg_vx_over_qin.png')
    plt.show()


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
    plt.savefig('graphs/avg_t_vs_qin.png')
    plt.show()

data = parse_output_files('output')
plot_avg_vx_over_qin(data)
plot_avg_t_vs_qin(data)

def load_file(path):
    """
    Lee un run_<qin>_<rep>.csv y devuelve un DataFrame:
        time  mean_abs_vx  qin  rep
    con la serie ⟨|vx|⟩(t) para ese run.
    """
    m = re.search(r'run_(\d+)_(\d+)\.csv', path.name)
    qin, rep = int(m.group(1)), int(m.group(2))

    df = pd.read_csv(path)
    out_dt = df['time'].drop_duplicates().diff().dropna().iloc[0]
    shift  = int(round(WINDOW / out_dt))   # 1 / 0.01

    # |vx| como Δx en 1 s
    df['x_prev'] = df.groupby('id')['x'].shift(shift)
    df.dropna(subset=['x_prev'], inplace=True)
    df['abs_vx'] = (df['x'] - df['x_prev']).abs() / WINDOW

    # ⟨|vx|⟩(t) para este run
    ts = (df.groupby('time')['abs_vx']
          .mean()
          .reset_index(name='mean_abs_vx'))
    ts['qin'], ts['rep'] = qin, rep
    return ts

all_ts = pd.concat(
    [load_file(Path(p)) for p in glob.glob(f"{OUT_DIR}/run_*.csv")],
    ignore_index=True)

# ---------- Evolución temporal ----------
plt.figure(figsize=(7,4))
for qin, g in all_ts.groupby('qin'):
    g_mean = g.groupby('time')['mean_abs_vx'].mean()
    plt.plot(g_mean.index, g_mean.values, label=f'Qin={qin}/s')

plt.xlabel('t [s]')
plt.ylabel(r'$\langle |v_x| \rangle$ [m/s]')
plt.xlim(0, max(all_ts.time))
plt.legend()
plt.tight_layout()
plt.grid(alpha=.3)
plt.savefig(f"{graphs_folder}/vx_time_series.png", dpi=150)

# ---------- < |vx| > 10–40 s con barras ----------
mask = (all_ts.time >= T1) & (all_ts.time <= T2)
# promedio 10–40 s por run
run_means = (all_ts[mask]
             .groupby(['qin','rep'])['mean_abs_vx']
             .mean()
             .reset_index())
# para cada Qin: media y error estándar (SEM) sobre las réplicas
summary = (run_means
           .groupby('qin')['mean_abs_vx']
           .agg(mean='mean', sem=lambda x: x.std(ddof=1)/np.sqrt(len(x)))
           .reset_index())

plt.figure(figsize=(5,4))
plt.plot(summary['qin'], summary['mean'],
         lw=1.2, marker='o', markersize=4, color='C0', zorder=3)
plt.errorbar(summary['qin'], summary['mean'],
             yerr=summary['sem'],
             fmt='none',
             ecolor='k', elinewidth=2, capsize=6,
             zorder=2)

plt.xlabel('Qin [1/s]')
plt.ylabel(r'$\langle |v_x| \rangle_{10-40\ \mathrm{s}}\ $ [m/s]')
plt.ylim(summary['mean'].min()*0.95, summary['mean'].max()*1.05)
plt.grid(alpha=.3)
plt.tight_layout()
plt.savefig(f'{graphs_folder}/vx_vs_qin.png', dpi=150)

# CSV con resultados
summary.to_csv(f"{graphs_folder}/vx_vs_qin.csv", index=False)
print("✓ Listo: gráficos y tabla guardados en", graphs_folder)

WIDTH  = 2.0
LENGTH = 10.0
AREA   = WIDTH * LENGTH
dfs = []
for path in glob.glob(f"{OUT_DIR}/run_*.csv"):
    m = re.search(r'run_(\d+)_(\d+)\.csv', Path(path).name)
    qin, rep = int(m.group(1)), int(m.group(2))
    # sólo necesito time e id para la densidad
    df = pd.read_csv(path, usecols=['time', 'id'])
    df['qin'], df['rep'] = qin, rep
    dfs.append(df)

df_all_particles = pd.concat(dfs, ignore_index=True)
# nº de partículas vivas por tiempo y réplica
pop_ts = (df_all_particles
          .groupby(['qin', 'rep', 'time'])
          ['id']
          .nunique()
          .reset_index(name='N'))

pop_ts['density'] = pop_ts['N'] / AREA
# combinar con velocidad promedio
merged = (all_ts.merge(pop_ts, on=['qin','rep','time']))
# foco en la ventana temporal 10–40 s
mask = (merged.time >= 10) & (merged.time <= 40)
subset = merged[mask]

# ---------- UNA CURVA POR Qin --------------------
plt.figure(figsize=(6,4))
binned_all = []
for (q, g) in subset.groupby('qin'):
    # bins automáticos
    bins = np.histogram_bin_edges(g['density'], bins='fd')
    labels = (bins[:-1] + bins[1:]) / 2
    g_binned = (g.assign(bin=pd.cut(g['density'], bins, labels=labels))
                .dropna(subset=['bin'])
                .groupby('bin', observed=False)['mean_abs_vx']
                .agg(['mean','std','count'])
                .reset_index()
                .astype({'bin':'float'}))

    sem = g_binned['std']
    plt.errorbar(g_binned['bin'], g_binned['mean'], yerr=sem, fmt='o-', capsize=4,
                 label=f'Qin={q}/s')

    g_binned.insert(0, 'qin', q)
    binned_all.append(g_binned)

plt.xlabel(r'Densidad [peatones/m$^{2}$]')
plt.ylabel(r'$\langle |v_x| \rangle$ [m/s]')
plt.grid(alpha=.3)
plt.tight_layout()
plt.legend(title='Caudal de entrada')
plt.savefig(f'{graphs_folder}/fundamental_multiQin.png', dpi=150)

pd.concat(binned_all, ignore_index=True) \
    .to_csv(f'{graphs_folder}/fundamental_multiQin.csv', index=False)
print("✓ Diagrama fundamental guardado en graphs")

