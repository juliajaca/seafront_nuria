# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# %%
sst = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/SST_AR4_timeseries_Balear.dat', delim_whitespace=True, header=None, skiprows=1)
df_sst =sst.iloc[:, [0, 1]]

parche = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/prueba_runup_años.csv')

# %%
parche_lineal = parche.copy()
# %%
parche[2025] =  674 + 24.4 * parche['profundidad'] 
for año in range(2026, 2100):
    valor_modelo = df_sst.loc[df_sst.iloc[:, 0] == año]
    sst = float(valor_modelo.iloc[0, 1])  # Primera fila, segunda columna
    print(sst)
    d_anterior = parche.iloc[:,-1:]
    r = d_anterior * 0.05 #por año
    m_temp =  d_anterior* (0.021 * sst - 0.471)
    m_frente = 0.07 * d_anterior
    d_año = d_anterior + r  - m_temp - m_frente
    parche[año] = d_año
    # print(valor_modelo)
    # print(type(valor_modelo))
    print('---')

# %% AJUSTE LINEAl
# Extraer los valores (asumiendo que la primera columna es el año y la segunda los valores)
años = df_sst.iloc[:, 0]  # Primera columna (años)
valores = df_sst.iloc[:, 1]  # Segunda columna (valores a ajustar)

# Ajuste lineal
m, b = np.polyfit(años, valores, 1)
# Crear valores ajustados
ajuste = m * años + b

# %%
df_sst['lineal'] = ajuste
# %%
parche_lineal[2025] =  674 + 24.4 * parche_lineal['profundidad'] 
for año in range(2026, 2100):
    valor_modelo = df_sst.loc[df_sst.iloc[:, 0] == año]
    print(valor_modelo)
    sst = valor_modelo['lineal'].iloc[0]  # Primera fila, segunda columna
    print(sst)
    d_anterior = parche_lineal.iloc[:,-1:]
    print('la densidad enterior es ', d_anterior)
    r = d_anterior * 0.05 # por año
    m_temp =  d_anterior* (0.021 * sst - 0.471)
    m_frente = 0.07 * d_anterior
    d_año = d_anterior + r  - m_temp - m_frente
    parche_lineal[año] = d_año
    # print(valor_modelo)
    # print(type(valor_modelo))
    print('---')

# %% PLTOTS
plt.figure(figsize=(8, 5))
plt.plot(df_sst.iloc[:, 0], df_sst.iloc[:, 1], marker="o", linestyle="-", color="b", label="SST_curva")
plt.plot(df_sst.iloc[:, 0], df_sst['lineal'], marker="o", linestyle="-", color="r", label="SST_Lineal")
plt.xlabel("Año")
plt.ylabel("SST")
plt.title("Evolución de la SST ")
plt.legend()
plt.show()

# %%
columnas_años = parche.columns[3:] 
suma_densidades = parche[columnas_años].sum()
columnas_años_lineal = parche_lineal.columns[3:] 
suma_densidades_lineal = parche_lineal[columnas_años].sum()

# %%
plt.figure(figsize=(10, 5))
plt.plot(suma_densidades.index, suma_densidades.values, marker="o", linestyle="-", color="b", label="Suma de densidades curva")
plt.plot(suma_densidades_lineal.index, suma_densidades_lineal.values, marker="o", linestyle="-", color="r", label="Suma de densidades lineal" )
plt.xlabel("Año")
plt.ylabel("Suma de densidades")
plt.title("suma densidad vs tiempo")
plt.xticks(rotation=45)
plt.legend()
plt.show()

# %%
# posiciones 2 a -9, 235 a -5 y 750 a -1.4
plt.figure(figsize=(8, 5))
plt.plot(columnas_años, parche.iloc[2, 3:] , marker="o", linestyle="-", color="orange", label="SST_curva a -9", alpha = 0.5)
plt.plot(columnas_años, parche_lineal.iloc[2, 3:] , marker="o", linestyle="-", color="red", label="SST_lineal a -9", alpha= 0.5)

plt.plot(columnas_años, parche.iloc[235, 3:] , marker="o", linestyle="-", color="gold", label="SST_curva a -5", alpha = 0.5)
plt.plot(columnas_años, parche_lineal.iloc[235, 3:] , marker="o", linestyle="-", color="yellow", label="SST_lineal a -5", alpha= 0.5)

plt.plot(columnas_años, parche.iloc[750, 3:] , marker="o", linestyle="-", color="green", label="SST_curva a -1.4", alpha = 0.5)
plt.plot(columnas_años, parche_lineal.iloc[750, 3:] , marker="o", linestyle="-", color="lime", label="SST_lineal a -1.4", alpha= 0.5)

plt.xlabel("Año")
plt.ylabel("Densidad")
plt.title("Evolución de la Densidad en tres puntos del parche ")
plt.legend()
plt.show()

# %%
