# %%
import pandas as pd
import subprocess
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
# import mat73
from Playa import Playa
from Modelo import Modelo
# from Parche import Parche
path_xbeach = 'C:/Users/Julia/Documents/XBeach_1.24.6057_Halloween_win64_netcdf/XBeach_1.24.6057_Halloween_win64_netcdf/xbeach.exe'
path_ficheros_ejecucion =  'C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/1_xbeach/ficheros/'
tiempo_ejecucion = 1800
parametro_rt= 1800

# Valores miguel para pendiente
hmed = 0.6788
tmed = 5.2827
h99 = 2
t99= 10
inicio_pradera = -0.6
fin_pradera = -10
d50 = 0.0005
año = 2026
# d50 = 0.0005 # 0.5mm/1000 mm m-1

# playa almadrava
nombre= 'almadrava'
hmed = 0.3854
tmed = 4.9709
h99 = 2.0220
t99= 10.8696
inicio_pradera = -3.380359
fin_pradera = -24.12477
d50 = 0.314/1000

# Playa parazuelos
nombre = 'parazuelo'
hmed = 0.4177
tmed = 5.0876
h99 = 1.9308 
t99=  10.8696
inicio_pradera = -3
fin_pradera = -24
d50 = 0.97/1000


playa = Playa(hmed, tmed, h99, t99, d50, round(inicio_pradera, 0), round(fin_pradera,0))
# modelo = Modelo(playa, tiempo_ejecucion, parametro_rt, año)
# %%
# PLOT densidad vs profundidad
fig, ax = plt.subplots(figsize=(12, 6))
cmap = plt.cm.viridis  
norm = plt.Normalize(vmin=2025, vmax=2099)  # Normaliza los años
# Trazar las líneas, cada una con un color distinto
for year in playa.densidades.columns:
    ax.plot(playa.profundidades, playa.densidades[year], label=str(year), color=cmap(norm(year)))
# Agregar la barra de color
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])  # Necesario para que el colorbar funcione
cbar = plt.colorbar(sm, ax=ax, orientation='vertical', pad=0.02)
cbar.set_label('Año', rotation=270, labelpad=20)
ax.set_xlabel('Profundidad (m)')
ax.set_ylabel('Densidad')
ax.set_title('Densidad vs Profundidad para diferentes años')
plt.tight_layout()
plt.show()
# %% plot densidad vs tiempo
fig, ax = plt.subplots(figsize=(12, 6))
# Establecer un mapa de colores (colormap) para las distancias
cmap = plt.cm.viridis  # Puedes usar otros colormaps como 'plasma', 'inferno', 'magma', etc.
norm = plt.Normalize(vmin=playa.profundidades.min(), vmax=playa.profundidades.max())  # Normaliza las profundidades
# Trazar las líneas, cada una con un color distinto
for i, dist in enumerate(playa.profundidades):
    ax.plot(playa.densidades.columns, playa.densidades.iloc[i, :], label=f'Distancia {dist} m', color=cmap(norm(dist)))
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])  # Necesario para que el colorbar funcione
cbar = plt.colorbar(sm, ax=ax, orientation='vertical', pad=0.02)
cbar.set_label('Distancia (m)', rotation=270, labelpad=20)
ax.set_xlabel('Año')
ax.set_ylabel('Densidad')
ax.set_title('Densidad vs Año para diferentes distancias')
plt.tight_layout()
plt.show()

# %%
for año in range(2025,2099):
    print('--------------------------------------------------------------')
    print(f'el año es {año}')
    # print(*prueba.bed, sep="\n")
    modelo = Modelo(playa, tiempo_ejecucion, parametro_rt, año)

    # EJEUCUON XBEACH
    result = subprocess.run([path_xbeach], shell=True, capture_output=True, text=True, cwd= path_ficheros_ejecucion)
    print('fin de la ejecucion')
    print(result.stdout)

    # leer output
    ds = xr.open_dataset(path_ficheros_ejecucion+'xboutput.nc')
    print(ds)
    # '''
    # # plt.plot(ds.point_zs.values)
    # # lista_rus.append(ds.point_zs.values)
    # '''t64(-9.5), np.float64(-10.0)): 249.43465589500792,

    playa.ru = ds.point_zs.values
    indice = int( [ n for n,i in enumerate(playa.ru) if i>0.01 ][0] + 5*playa.t99)
    playa.zs = np.percentile(playa.ru[indice:],98)
    print('los rus son')
    valores = (ds.point_zs.values[indice:])
    print(valores)
    # plt.plot(playa.ru)
        
    print(f'dean-->{playa.dean} ru-->{playa.zs} h99-->{playa.h99} hmed-->{playa.h}')


    print('ya he terminado')
    np.savetxt(f"RU{nombre}_{año}.csv", playa.ru)

    print('ya he terminado')
    with open(f"RU{nombre}_{año}.txt", "w") as f:
        f.write(str(playa.zs))
#  %%