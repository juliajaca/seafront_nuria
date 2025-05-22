# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely import wkt
import matplotlib.ticker as mticker
import matplotlib.cm as cm
import matplotlib.colors as colors

# %%
densidades = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/_densidades_posidonia.csv')
#  deshacer el wkt
densidades["geometry"] = densidades["geometry"].apply(wkt.loads)
densidades = gpd.GeoDataFrame(densidades, geometry="geometry")

captura = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/_secuestro_carbono.csv')

captura_d = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/_secuestro_carbono_densidad.csv')

emisiones_hojas = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/_emisiones_hojas_carbono.csv')

emisiones_hojas_d = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/_emisiones_hojas_carbono_densidad.csv')

emisiones_stock= pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/_emisiones_stock_carbono.csv')




# %%
"""
U   U N   N     PPPP   AA  RRRR   CCC H  H EEEE
U   U NN  N     P   P A  A R   R C    H  H E
U   U N N N     PPPP  AAAA RRRR  C    HHHH EEE
U   U N  NN     P     A  A R R   C    H  H E
 UUU  N   N     P     A  A R  RR  CCC H  H EEEE
"""
df_filtrado = densidades.loc[(densidades['parche'] == 0.0) & (densidades['zona'] == 'baleares')]
# df.loc[(df['column_name'] >= A) & (df['column_name'] <= B)]

# Asegurarse de que 'geometry' sea una GeoSeries
gdf = gpd.GeoDataFrame(df_filtrado, geometry='geometry', crs= 'EPSG:4258')

# Años que quieres visualizar
años_objetivo = ['2025', '2050', '2075', '2099']
# años_objetivo = ['2025', ]

# Concatenar todos los valores para encontrar mínimo y máximo (evitar ceros o negativos en log)
valores_totales = pd.concat([gdf[año].astype(float).replace(0, np.nan) for año in años_objetivo])
vmin = valores_totales.min()
vmax = valores_totales.max()

# Crear figura con subplots
fig, axs = plt.subplots(2, 2, figsize=(12, 10),constrained_layout=True)

# Usar escala logarítmica
norm = colors.LogNorm(vmin=vmin, vmax=vmax)
cmap = cm.viridis

# Dibujar los plots
for ax, año in zip(axs.flat, años_objetivo):
    valores = gdf[año].astype(float).replace(0, np.nan)
    gdf.plot(ax=ax, column=valores, cmap=cmap, norm=norm, markersize=30)
    ax.set_title(f'Año {año}')
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f')) 

# Colorbar común logarítmica
sm = cm.ScalarMappable(norm=norm, cmap=cmap)
sm._A = []  # dummy array for colorbar
cbar = fig.colorbar(sm, ax=axs, location='right',)
cbar.set_label("Densidad (haces/m²) [escala log]")

plt.show()

# ----
df_filtrado = densidades.loc[(densidades['parche'] == 0.0) & (densidades['zona'] == 'baleares')]
gdf = gpd.GeoDataFrame(df_filtrado, geometry='geometry', crs= 'EPSG:4258')

años_objetivo = ['2025', '2050', '2075', '2099']

fig, axs = plt.subplots(2, 2, figsize=(12, 10))

for ax, año in zip(axs.flat, años_objetivo):
    valores = gdf[año].astype(float)
    gdf.plot(ax=ax, column=valores, cmap='viridis', legend=True,
             markersize=30, legend_kwds={'label': f'Densidad en {año} (haces/m²)'})
    ax.set_title(f'Año {año}')
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f'))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.4f')) 

plt.tight_layout()
plt.show()
# %%
"""
U   U N   N     PPPP  U   U N   N TTTTTT  OOO
U   U NN  N     P   P U   U NN  N   TT   O   O
U   U N N N     PPPP  U   U N N N   TT   O   O
U   U N  NN     P     U   U N  NN   TT   O   O
 UUU  N   N     P      UUU  N   N   TT    OOO
"""
años = [str(año) for año in range(2025, 2100)]
# Nombres personalizados para los ejes y las líneas
titulos = [
    "Densidad de Posidonia",
    "Captura de Carbono (kg/m²)",
    "Emisiones por hojas muertas (kg/m²)",
    "Emisiones por degradación del stock (kg/m²)"
]

labels = [
    "Densidad (haces/m²)",
    "Captura de carbono",
    "Emisión hojas",
    "Emisión stock"
]
# Lista de DataFrames
dfs = [densidades,  captura, emisiones_hojas, emisiones_stock]

fig, axs = plt.subplots(4, 1, figsize=(10, 12), sharex=True)
# Crear figura con 4 subplots (verticales)
for j, (df, ax) in enumerate(zip(dfs, axs)):
    valores = df.loc[0, años].astype(float).values
    ax.plot(años, valores, label=labels[j], color=f'C{j}')
    ax.set_title(titulos[j])
    ax.set_ylabel(labels[j])
    ax.grid(True)
    
    #
    if j == 1:
        valores = captura_d.loc[0, años].astype(float).values
        ax.plot(años, valores, label='Captura de carbono densidad', color='gold')
    elif j == 2:
        valores = emisiones_hojas_d.loc[0, años].astype(float).values
        ax.plot(años, valores, label='Emisión hojas densidad', color='darkgreen')
    ax.legend()
ticks_cada_5 = años[::5]
axs[-1].set_xticks(ticks_cada_5)
axs[-1].set_xlabel('Año')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
# %%
"""
PPPP   AA  RRRR   CCC H  H EEEE      CCC  OOO   22
P   P A  A R   R C    H  H E        C    O   O 2  2
PPPP  AAAA RRRR  C    HHHH EEE      C    O   O   2
P     A  A R R   C    H  H E        C    O   O  2
P     A  A R  RR  CCC H  H EEEE      CCC  OOO  2222
"""
# Lista de años como strings
años = [str(año) for año in range(2025, 2100)]

# Seleccionar el parche 0 en cada DataFrame
captura_0 = captura[(captura['parche'] == 0.0) & (captura['zona'] == 'baleares')]
emisiones_hojas_0 = emisiones_hojas[(emisiones_hojas['parche'] == 0.0) & (emisiones_hojas['zona'] == 'baleares')]
emisiones_stock_0 = emisiones_stock[(emisiones_stock['parche'] == 0.0) & (emisiones_stock['zona'] == 'baleares')]

# Sumar para cada año (por columnas)
suma_captura = captura_0[años].sum()
suma_hojas = emisiones_hojas_0[años].sum()
suma_stock = emisiones_stock_0[años].sum()

# Crear figuras
fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

# Lista de series y etiquetas
series = [suma_captura, suma_hojas, suma_stock]
titulos = [
    "Captura total de carbono en el parche",
    "Emisión total por hojas muertas en el parche",
    "Emisión total por degradación del stock en el parche"
]
labels = [
    "Captura (kg)",
    "Emisión hojas (kg)",
    "Emisión stock (kg)"
]

for i, (serie, ax) in enumerate(zip(series, axs)):
    ax.plot(años, serie.values, color=f'C{i}', label=labels[i])
    ax.set_title(titulos[i])
    ax.set_ylabel(labels[i])
    ax.grid(True)
    ax.legend()

# Ajuste de ticks cada 5 años
ticks_cada_5 = años[::5]
axs[-1].set_xticks(ticks_cada_5)
axs[-1].set_xlabel("Año")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
# %%
"""
EEEE  SSS  PPPP   AA   AA
E    S     P   P A  A A  A
EEE   SSS  PPPP  AAAA AAAA
E        S P     A  A A  A
EEEE SSSS  P     A  A A  A
"""
# Lista de años como strings
años = [str(año) for año in range(2025, 2100)]

# Sumar para cada año (por columnas)
suma_captura = captura[años].sum()
suma_hojas = emisiones_hojas[años].sum()
suma_captura_d = captura_d[años].sum()
suma_hojas_d = emisiones_hojas_d[años].sum()
suma_stock = emisiones_stock[años].sum()

# Crear figuras
fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

# Lista de series y etiquetas
series = [suma_captura, suma_hojas, suma_stock]
titulos = [
    "Captura total de carbono (España)",
    "Emisión total por hojas muertas",
    "Emisión total por degradación del stock"
]
labels = [
    "Captura (millones de kg)",
    "Emisión hojas (millones de kg)",
    "Emisión stock (millones de kg)"
]

for i, (serie, ax) in enumerate(zip(series, axs)):
    valores_millones = serie.values / 1e6  # Escalar a millones
    ax.plot(años, valores_millones, color=f'C{i}', label=labels[i])
    ax.set_title(titulos[i])
    ax.set_ylabel(labels[i])
    ax.grid(True)

    if i == 0:
        valores_millones = suma_captura_d.values / 1e6  # Escalar a millones
        ax.plot(años, valores, label='Captura de carbono densidad', color='gold')
    elif i == 1:
        valores_millones = suma_hojas_d.values / 1e6  # Escalar a millones
        ax.plot(años, valores, label='Emisión hojas densidad', color='darkgreen')

    ax.legend()
    ax.ticklabel_format(style='plain', axis='y')  # Forzar sin notación científica

# Ajuste de ticks cada 5 años
ticks_cada_5 = años[::5]
axs[-1].set_xticks(ticks_cada_5)
axs[-1].set_xlabel("Año")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()# %%

# %%
