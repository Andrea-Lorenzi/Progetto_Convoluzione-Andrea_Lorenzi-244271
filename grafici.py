import pandas as pd
import matplotlib.pyplot as plt

# 1. Caricamento dati
print("Caricamento di performance_log.csv...")

try:
    df = pd.read_csv('performance_log.csv')

except FileNotFoundError:
    print("ERRORE: File performance_log.csv non trovato. Esegui prima 'make test'.")
    exit(1)

# 2. Pulizia e preparazione dati
# Rimuove la 'x' dalla colonna Speedup e converte in numero decimale
df['Speedup'] = df['Speedup'].astype(str).str.replace('x', '').astype(float)

# Il Makefile calcola già la deviazione standard, ci assicuriamo sia float
df['Deviazione_Standard'] = df['Deviazione_Standard'].astype(float)

# Imposta uno stile di base pulito per i grafici
plt.style.use('ggplot')

# Filtriamo i dati per i primi 3 grafici in modo da usare solo la modalità Private ('P')
# altrimenti le medie verrebbero sballate dai tempi lenti della modalità Shared
df_ottimale = df[df['Variabili'] == 'P']

schedules = df_ottimale['Schedule'].unique()
dimensioni = df_ottimale['Dimensione'].unique()
threads_ticks = [1, 4, 8, 16, 32, 64, 128] # Aggiornato ai thread del Makefile

print("Generazione dei grafici in corso...")

# ==========================================================
# GRAFICO 1: Speedup vs Thread (3 subplots per i 3 schedule)
# ==========================================================
fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
fig.suptitle('Speedup in funzione dei Thread (Variabili Private)', fontsize=16, fontweight='bold')

for i, sched in enumerate(schedules):
    ax = axes[i]
    df_sched = df_ottimale[df_ottimale['Schedule'] == sched]
    
    for dim in dimensioni:
        df_dim = df_sched[df_sched['Dimensione'] == dim]
        ax.plot(df_dim['Thread'], df_dim['Speedup'], marker='o', label=f'{dim}x{dim}')
        
    ax.set_title(f'Schedule: {sched}')
    ax.set_xlabel('Numero di Thread')
    if i == 0:
        ax.set_ylabel('Speedup')
    
    ax.set_xticks(threads_ticks)
    ax.axhline(1, color='black', linestyle='--', linewidth=1.2) # Linea base sequenziale
    ax.legend()

plt.tight_layout()
plt.savefig('01_grafico_speedup.png', dpi=300)
plt.close()

# =========================================================
# GRAFICO 2: Tempi di esecuzione in Scala Logaritmica
# =========================================================
plt.figure(figsize=(10, 6))

# Usiamo lo schedule 'dynamic' come campione rappresentativo
for dim in dimensioni:
    df_dim = df_ottimale[(df_ottimale['Dimensione'] == dim) & (df_ottimale['Schedule'] == 'dynamic')]
    plt.errorbar(df_dim['Thread'], df_dim['Tempo_Par(s)'], yerr=df_dim['Deviazione_Standard'], 
                 marker='s', capsize=4, linewidth=2, label=f'Dim: {dim}')

plt.title('Tempi di Esecuzione - Schedule Dynamic (Variabili Private)', fontsize=14, fontweight='bold')
plt.xlabel('Numero di Thread')
plt.ylabel('Tempo Parallelo (secondi) - Scala Log')
plt.yscale('log')
plt.xticks(threads_ticks)
plt.legend()
plt.tight_layout()
plt.savefig('02_grafico_tempi_log.png', dpi=300)
plt.close()

# ====================================================
# GRAFICO 3: Confronto Schedule a barre (Matrice 4096)
# ====================================================
df_4096 = df_ottimale[df_ottimale['Dimensione'] == 4096]

# Riorganizza i dati per il grafico a barre
pivot_4096 = df_4096.pivot(index='Thread', columns='Schedule', values='Speedup')

ax = pivot_4096.plot(kind='bar', figsize=(10, 6), width=0.7)
plt.title('Confronto delle Policy di Scheduling (Matrice 4096x4096, Private)', fontsize=14, fontweight='bold')
plt.xlabel('Numero di Thread')
plt.ylabel('Speedup')
plt.xticks(rotation=0)
plt.axhline(1, color='black', linestyle='--', linewidth=1.2)
plt.legend(title='Policy')

plt.tight_layout()
plt.savefig('03_confronto_schedule.png', dpi=300)
plt.close()

# ================================
# GRAFICO 4: Private vs Shared
# ================================
plt.figure(figsize=(10, 6))

# Prendiamo una matrice fissa e uno schedule fisso
dim_scelta = 2048
df_confronto = df[(df['Dimensione'] == dim_scelta) & (df['Schedule'] == 'static')]

df_private = df_confronto[df_confronto['Variabili'] == 'P']
df_shared = df_confronto[df_confronto['Variabili'] == 'S']

plt.plot(df_private['Thread'], df_private['Tempo_Par(s)'], marker='o', color='green', linewidth=2, label='Private (Ottimale)')
plt.plot(df_shared['Thread'], df_shared['Tempo_Par(s)'], marker='x', color='red', linewidth=2, linestyle='--', label='Shared (Conflitto)')

plt.title(f'Impatto della gestione Memoria: Private vs Shared (Dim: {dim_scelta})', fontsize=14, fontweight='bold')
plt.xlabel('Numero di Thread')
plt.ylabel('Tempo Parallelo (secondi)')
plt.xticks(threads_ticks)
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig('04_confronto_memoria.png', dpi=300)
plt.close()

print("Fatto! I 4 grafici sono stati salvati come immagini PNG ad alta risoluzione (300 DPI).")