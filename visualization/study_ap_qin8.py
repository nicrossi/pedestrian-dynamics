import re, glob, os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

# Qin = 8, barrido de A_p con varias corridas
OUT_DIR       = "output"
GRAPHS_DIR    = "graphs"
WINDOW        = 1.0               # s para |vx|
T_AVG         = (10.0, 40.0)      # intervalo de promediado
Q_TARGET      = 8
os.makedirs(GRAPHS_DIR, exist_ok=True)

PAT = re.compile(rf'run_{Q_TARGET}_(\d+)_([\d\.]+)\.csv')

def load_run(path: Path):
    m = PAT.match(path.name)
    if not m:
        return None, None
    rep, Ap = m.group(1), float(m.group(2))

    df = pd.read_csv(path)
    dt = df['time'].drop_duplicates().diff().dropna().iloc[0]
    shift = int(round(WINDOW / dt))

    df['x_prev'] = df.groupby('id')['x'].shift(shift)
    df.dropna(subset=['x_prev'], inplace=True)
    df['abs_vx'] = (df['x'] - df['x_prev']).abs() / WINDOW

    ts = (df.groupby('time')['abs_vx']
          .mean()
          .reset_index(name='mean_abs_vx'))
    ts['Ap'], ts['rep'] = Ap, rep
    return ts, df['time'].max()

records, tf_rows = [], []
for p in glob.glob(f"{OUT_DIR}/run_{Q_TARGET}_*.csv"):
    ts, tf = load_run(Path(p))
    if ts is not None:
        records.append(ts)
        tf_rows.append({'Ap': ts['Ap'].iat[0], 'rep': ts['rep'].iat[0], 'tf': tf})

if not records:
    raise RuntimeError("No se encontraron runs para Qin = 8")

ts_all = pd.concat(records, ignore_index=True)
tf_df  = pd.DataFrame(tf_rows)

# ---------------- FIG 1 — evolución temporal con escala secuencial ---------
plt.figure(figsize=(7,4))

ap_values = np.sort(ts_all['Ap'].unique())
cmap = plt.cm.RdYlGn
# centro en Ap = 1.1; extremos en min/max presentes
norm = TwoSlopeNorm(vmin=ap_values.min(),
                    vcenter=1.1,
                    vmax=ap_values.max())

for Ap in ap_values:
    g = ts_all[ts_all.Ap == Ap]
    g_mean = g.groupby('time')['mean_abs_vx'].mean()
    plt.plot(g_mean.index, g_mean.values,
             color=cmap(norm(Ap)),
             label=f'Aₚ={Ap:.2f}')

plt.xlabel('t [s]')
plt.ylabel(r'$\langle|v_x|\rangle$ [m/s]')
plt.grid(alpha=.3)
plt.tight_layout()

ax = plt.gca()
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
plt.colorbar(sm, ax=ax, pad=0.02).set_label(r'$A_p$')

plt.savefig(f'{GRAPHS_DIR}/vx_time_Ap_q8.png', dpi=150)
plt.close()

t1, t2 = T_AVG
mask = (ts_all.time >= t1) & (ts_all.time <= t2)

run_means = (ts_all[mask]
             .groupby(['Ap','rep'])['mean_abs_vx']
             .mean()
             .reset_index())

def sem_flexible(group):
    if len(group) > 1:                              # ≥2 réplicas
        return group.std(ddof=1) / np.sqrt(len(group))
    ap = group.name
    single_rep = ts_all[(ts_all.Ap == ap) & mask]['mean_abs_vx']
    return single_rep.std(ddof=1) / np.sqrt(len(single_rep))

vx_summary = (run_means
              .groupby('Ap')['mean_abs_vx']
              .agg(mean='mean', sem=sem_flexible)
              .reset_index()
              .sort_values('Ap'))

plt.figure(figsize=(5,4))
plt.errorbar(vx_summary['Ap'], vx_summary['mean'],
             yerr=vx_summary['sem'], fmt='o-', capsize=5)
plt.xlabel(r'$A_p$', fontsize=15)
plt.ylabel(r'$\langle|v_x|\rangle_{10-40\ \mathrm{s}}$ [m/s]', fontsize=15)
plt.grid(alpha=.3); plt.tight_layout()
plt.savefig(f'{GRAPHS_DIR}/vx_vs_Ap_q8.png', dpi=150)
plt.close()

tf_summary = (tf_df
              .groupby('Ap')['tf']
              .agg(mean='mean', sem=lambda x: x.std(ddof=1)/np.sqrt(len(x)))
              .reset_index()
              .sort_values('Ap'))

plt.figure(figsize=(5,4))
plt.errorbar(tf_summary['Ap'], tf_summary['mean'],
             yerr=tf_summary['sem'], fmt='o-', capsize=5, color='C2')
plt.xlabel(r'$A_p$', fontsize=15)
plt.ylabel(r'$\langle t_f\rangle$ [s]', fontsize=15)
plt.grid(alpha=.3); plt.tight_layout()
plt.savefig(f'{GRAPHS_DIR}/tf_vs_Ap_q8.png', dpi=150)
plt.close()

summary = vx_summary.merge(tf_summary, on='Ap',
                           suffixes=('_vx','_tf'))
summary.to_csv(f'{GRAPHS_DIR}/Ap_q8_summary.csv', index=False)

print("✓ Figuras y tabla guardadas en", GRAPHS_DIR)
