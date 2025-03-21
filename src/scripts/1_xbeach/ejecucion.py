# %%
import pandas as pd
import subprocess
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
# import mat73
from Playa import Playa
from Modelo import Modelo
path_xbeach = 'C:/Users/Julia/Documents/XBeach_1.24.6057_Halloween_win64_netcdf/XBeach_1.24.6057_Halloween_win64_netcdf/xbeach.exe'
path_ficheros_ejecucion =  'C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/1_xbeach/ficheros/'
tiempo_ejecucion = 1800
parametro_rt= 1800

# Valores miguel para pendiente
hmed = 0.6788
tmed = 5.2827
h99 = 2
t99= 10
inicio_pradera = -3
fin_pradera = -10
d50 = 0.0005
# d50 = 0.0005 # 0.5mm/1000 mm m-1

# %%
playa = Playa(hmed, tmed, h99, t99, d50,  inicio_pradera, fin_pradera)
# print(*prueba.bed, sep="\n")
modelo = Modelo(playa, tiempo_ejecucion, parametro_rt, 2025)

# %% EJEUCUON XBEACH
result = subprocess.run([path_xbeach], shell=True, capture_output=True, text=True, cwd= path_ficheros_ejecucion)
print('fin de la ejecucion')
print(result.stdout)

# %%
# leer output
ds = xr.open_dataset(path_ficheros_ejecucion+'xboutput.nc')
print(ds)
# '''
# # plt.plot(ds.point_zs.values)
# # lista_rus.append(ds.point_zs.values)
# '''

playa.ru = ds.point_zs.values
indice =  [ n for n,i in enumerate(playa.ru) if i>0.01 ][0] + 5*playa.t99
playa.zs = np.percentile(playa.ru[indice:],98)
print('los rus son')
valores = (ds.point_zs.values[indice:])
print(valores)
plt.plot(playa.ru)
    
print(f'dean-->{playa.dean} ru-->{playa.zs} h99-->{playa.h99} hmed-->{playa.h}')

# %%
print('ya he terminado')
np.savetxt(f"RU_densidad_cambiante_{inicio_pradera}_{fin_pradera}.csv", playa.ru)

# %%
print('ya he terminado')
with open(f"RU_densidad_cambiante_{inicio_pradera}_{fin_pradera}.txt", "w") as f:
    f.write(str(playa.zs))
# %%