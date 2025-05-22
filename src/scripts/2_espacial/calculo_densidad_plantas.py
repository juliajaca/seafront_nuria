import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# %%
sst = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/SST_AR4_timeseries_Balear.dat', delim_whitespace=True, header=None, skiprows=1)
df_sst =sst.iloc[:, [0, 1]]

parche_cat = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/bat_parches_cat.csv')
parche_bal = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/bat_parches_bal.csv')
parche_pen = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/bat_parches_pen.csv')

# %%
parche = pd.concat([parche_bal, parche_cat, parche_pen], ignore_index=True)


# %%
#  la densidad inicial
parche[2025] =  674 + 24.4 * parche['profundidad'] 

for año in range(2026, 2100):
    valor_modelo = df_sst.loc[df_sst.iloc[:, 0] == año]
    sst = float(valor_modelo.iloc[0, 1])  # Primera fila, segunda columna
    print(sst)
    d_anterior = parche.iloc[:,-1:]
    r = d_anterior * 0.05 # reclutamento por año
    m_temp =  d_anterior* (0.021 * sst - 0.471) #muerte por calo
    m_frente = 0.07 * d_anterior # muerte del frente

    d_año = d_anterior + r  - m_temp - m_frente
    parche[año] = d_año
    # print(valor_modelo)
    # print(type(valor_modelo))
    print('---')
print('fin')
#  %%
parche.to_csv("_densidades_posidonia.csv", index=False)
# %%
