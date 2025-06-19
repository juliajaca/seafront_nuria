# %%
import pandas as pd
import numpy as np
import os
from shapely.wkt import loads
import matplotlib.pyplot as plt
import sys
sys.path.append(os.path.abspath("C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/5_xbeach_temporal"))
from carga_datos_temp import devolver_sst2




# %%
sst = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/SST_AR4_timeseries_Balear.dat', delim_whitespace=True, header=None, skiprows=1)
df_sst =sst.iloc[:, [0, 1]]

parche_cat = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/bat_parches_cat.csv')
parche_bal = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/bat_parches_bal.csv')
parche_pen = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/bat_parches_pen.csv')

# %%
parches = pd.concat([parche_bal, parche_cat, parche_pen], ignore_index=True)


# %%
#  la densidad inicial
parches["geometry"] = parches["geometry"].apply(loads)
# %%
# parches[2025] =  674 + 24.4 * parches['profundidad'] 
# %%
todo_densidades = []
for i in range(len(parches)):
    densidades = [674 + 24.4 * parches.iloc[i]['profundidad'] ] 
    print(f'para el parche {i} la densidad inicial es {densidades}')

    for año in range(2026, 2100):                
        sst = devolver_sst2(parches.iloc[i]['geometry'].y,
                            parches.iloc[i]['geometry'].x , 
                            año)
    
        d_anterior = densidades[-1]
        # print(d_anterior)
        r = d_anterior * 0.05 # reclutamento por año
        m_temp =  d_anterior* (0.021 * sst - 0.471) #muerte por calo
        # print(f'la muerte por temp es {m_temp}')
        m_frente = 0.07 * d_anterior # muerte del frente

        d_año = d_anterior + abs(r)  - abs(m_temp) - abs( m_frente)
        densidades.append(d_año)
        # print(valor_modelo)
        # print(type(valor_modelo))
        # print(d_año, año)
        # print('---')
    todo_densidades.append(densidades)
    print(f'las densidades son {densidades}')
print('fin')
# %%
array_datos = np.array(todo_densidades)
años = range(2025, 2025 + array_datos.shape[1])
df_nuevo = pd.DataFrame(array_datos, columns=años)
df = pd.concat([parches, df_nuevo], axis=1)

# %%
# parches[2025] =  674 + 24.4 * parches['profundidad'] 
# for año in range(2026, 2100):

#     valor_modelo = df_sst.loc[df_sst.iloc[:, 0] == año]
#     sst = float(valor_modelo.iloc[0, 1])  # Primera fila, segunda columna
#     print(sst)
#     d_anterior = parches.iloc[:,-1:]
#     print(d_anterior)
#     r = d_anterior * 0.05 # reclutamento por año
#     m_temp =  d_anterior* (0.021 * sst - 0.471) #muerte por calo
#     m_frente = 0.07 * d_anterior # muerte del frente

#     d_año = d_anterior + r  - m_temp - m_frente
#     parches[año] = d_año
#     # print(valor_modelo)
#     # print(type(valor_modelo))
#     print('---')
# print('fin')
#  %%
parches.to_csv("_densidades_posidonia_sst_en_tres_partes.csv", index=False)
# %%
