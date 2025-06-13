import os, csv, glob, re
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

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

    plt.errorbar(sorted_qin, avg_time_values, yerr=std_error_time_values, fmt='-o', capsize=5)
    plt.xlabel('Qin [1/s]', fontsize=15)
    plt.ylabel('Tiempo Máx. Promedio [s]', fontsize=15)
    plt.tight_layout()
    plt.grid(True)
    plt.savefig('graphs/avg_t_vs_qin.png')

data = parse_output_files('output')
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

### Ex b
plt.figure(figsize=(7,4))
for qin, g in all_ts.groupby('qin'):
    g_mean = g.groupby('time')['mean_abs_vx'].mean()
    plt.plot(g_mean.index, g_mean.values, label=f'Qin={qin}/s')

plt.xlabel('t [s]', fontsize=15)
plt.ylabel(r'$\langle |v_x| \rangle$ [m/s]', fontsize=15)
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

plt.xlabel('Qin [1/s]', fontsize=15)
plt.ylabel(r'$\langle |v_x| \rangle_{10-40\ \mathrm{s}}\ $ [m/s]', fontsize=15)
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

# 1) paleta secuencial: viridis (puedes cambiarla)
qin_vals = np.sort( merged['qin'].unique().astype(int) )
cmap  = plt.cm.viridis
norm  = plt.Normalize(vmin=qin_vals.min(), vmax=qin_vals.max())

binned_all = []

for q, g in merged.groupby('qin'):
    # --- binning ---
    bins   = np.histogram_bin_edges(g['density'], bins='fd')
    labels = (bins[:-1] + bins[1:]) / 2
    g_binned = (g.assign(bin=pd.cut(g['density'], bins, labels=labels))
                .dropna(subset=['bin'])
                .groupby('bin', observed=False)['mean_abs_vx']
                .agg(['mean','std','count'])
                .reset_index()
                .astype({'bin':'float'}))

    # --- inserta ρ=0 para continuidad ---
    if g_binned['bin'].iloc[0] > 0:
        first = g_binned.iloc[0].copy()
        first['bin'] = 0
        g_binned = pd.concat([first.to_frame().T, g_binned],
                             ignore_index=True)

    g_binned = g_binned.sort_values('bin')

    # --- curva continua con color secuencial ---
    plt.plot(g_binned['bin'], g_binned['mean'],
             lw=1.8, color=cmap(norm(int(q))),    # ← color depende de qin
             label=f'Qin={q}/s')

    g_binned.insert(0,'qin', q)
    binned_all.append(g_binned)

plt.xlabel(r'Densidad [peatones/m$^{2}$]', fontsize=15)
plt.ylabel(r'$\langle |v_x| \rangle$ [m/s]', fontsize=15)
plt.grid(alpha=.3)
plt.tight_layout()

# opcional: barra de color para explicar la escala
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])

ax  = plt.gca()                                      # eje principal
cax = inset_axes(ax, width="35%", height="4%",       # ← tamaño relativo
                 loc='upper right', borderpad=0.6)   # ← dentro del gráfico
cbar = plt.colorbar(sm, cax=cax, orientation='horizontal')
cbar.set_label('Qin [1/s]', fontsize=8)
cax.tick_params(labelsize=7)

plt.savefig(f'{graphs_folder}/fundamental_multiQin.png', dpi=150)

pd.concat(binned_all, ignore_index=True) \
    .to_csv(f'{graphs_folder}/fundamental_multiQin.csv', index=False)
print("✓ Diagrama fundamental guardado en graphs")


SCATTER_ALPHA, POINT_SIZE, RED = 0.3, 2, '#d62728'

for q, g in merged.groupby('qin'):
    fig, ax = plt.subplots(figsize=(4.5,3.5), dpi=300)

    # ---------- 1) nube de puntos ----------
    ax.scatter(g['density'], g['mean_abs_vx'],
               s=POINT_SIZE, color='C0',
               alpha=SCATTER_ALPHA, linewidths=0, zorder=1)

    # ---------- 2) curva binned ----------
    bins   = np.histogram_bin_edges(g['density'], bins='fd')
    labels = (bins[:-1] + bins[1:]) / 2
    g_b = (g.assign(bin=pd.cut(g['density'], bins, labels=labels))
           .dropna(subset=['bin'])
           .groupby('bin', observed=False)['mean_abs_vx']
           .agg(['mean','std','count'])
           .reset_index()
           .astype({'bin':'float'}))
    if g_b['bin'].iloc[0] > 0:
        first = g_b.iloc[0].copy()
    first['bin'] = 0
    g_b = pd.concat([first.to_frame().T, g_b],
                    ignore_index=True).sort_values('bin')
    ax.plot(g_b['bin'], g_b['mean'], lw=2, color=RED, zorder=3)

    # ---------- 3) estética ----------
    ax.set_xlabel(r'Density [1/m$^{2}$]' , fontsize=15)
    ax.set_ylabel(r'Velocity [m/s]', fontsize=15)
    ax.set_xlim(0, g['density'].max()*1.05)               # <<< xmin = 0
    ax.set_ylim(0, g['mean_abs_vx'].max()*1.10)

    ax.grid(alpha=.3)
    ax.set_title(f'Qin = {q} 1/s', fontsize=11)

    fig.tight_layout()
    fig.savefig(f'{graphs_folder}/fundamental_Q{q}_allT.png', dpi=300)
    plt.close(fig)