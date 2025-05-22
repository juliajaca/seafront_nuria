'''
perdona por el retraso en enviarte estos valores (no tengo los SE de los valores promedio):

- Stock organic carbon top 1st meter sediment (kg OC m-2) (fuente: Leiva et al submitted): Avg = 16.82    

- Stock carbono en hojas de Posidonia (kg OC m-2) (fuente: Leiva et al submitted): Avg = 0.03    

- Organic carbon sequestration rate (i.e. rate of carbon accumulation in the sediment - este es el carbono orgánico que se acumula a largo plazo) (kg OC m-2 yr-1) (fuente: Leiva et al submitted): Avg = 0.03   

Respecto a las emisiones de CO2 al perderse la pradera:

- que yo sepa, solo hay los valores del artículo adjunto de Roca et al 2022 medidos en un experimento que duró 3 meses (puedes usar los valores de CO2 efflux de la tabla 1); puedes usar un valor promedio de los dos tratamientos (agitado y reposo) y del rango de temperatura 26-29 oC (0.597 umol CO2 m-2 s-1) o ampliarlo hasta 32 oC (0.631 umol CO2 m-2 s-1) en función de las temperaturas de los escenarios. En este experimento solo incluimos temperaturas de verano, y al haber un efecto de la temperatura cabe esperar que en invierno las emisiones serán mas bajas o quizás insignificantes… Se deberían aplicar estos valores solo a los meses de verano (desde junio a septiembre, ambos incluidos)

- otra forma de estimar emisiones, que es la que se está utilizando por falta de estimas reales, es asumir que una vez se muere la pradera se puede erosionar el  carbono orgánico de los primeros 50 cm de sedimento y de este solo se remineraliza el 50 % a una tasa exponencial de 0.18 yr-1 (te paso un artículo en el que utilizan esta aproximación);
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# %%
df = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/_densidades_posidonia.csv')
# %%
oc_secuestrado = 0.03 #kilos por m2 y año hasta 60 de densidad

años = [str(a) for a in range(2025, 2100)]

# copia del DataFrame con solo los años
captura = df[años].copy()

# lógica de captura de carbono
# Si densidad >= 60, entonces captura = 0.03 * m2_punto, si no, 0

# Multiplicamos por la superficie del punto si cumple la condición
for año in años:
    captura[año] = np.where(df[año].astype(float) >= 60, 0.03 * df["m2_punto"], 0.0)

# %%
captura["geometry"] = df["geometry"]
captura["zona"] = df["zona"]
captura["parche"] = df["parche"]
captura["m2_punto"] = df["m2_punto"]

columnas_ordenadas = ["geometry", "zona", "parche", "m2_punto"] + años
captura = captura[columnas_ordenadas]
# %%
# captura.to_csv("_secuestro_carbono.csv", index=False)
# %%
"""
EEEE M   M III  SSS  III  OOO  N   N     H  H  OOO      J  AA   SSS
E    MM MM  I  S      I  O   O NN  N     H  H O   O     J A  A S
EEE  M M M  I   SSS   I  O   O N N N     HHHH O   O     J AAAA  SSS
E    M   M  I      S  I  O   O N  NN     H  H O   O J   J A  A     S
EEEE M   M III SSSS  III  OOO  N   N     H  H  OOO   JJJ  A  A SSSS
"""
# Crear DataFrame vacío para emisiones
emisiones = pd.DataFrame(0.0, index=df.index, columns=años)

for i, row in df.iterrows():
    m2 = row["m2_punto"]
    vivo = True if float(row['2025']) >= 60 else False

    id_año = 0

    while id_año < len(años)-1 and vivo:

        año = años[id_año]
        siguiente = años[id_año+1]
        densidad = float(row[año])  

        if  densidad < 60:
            # La pradera muere este año, emite el siguiente
            emisiones.at[i, siguiente] = 0.03 * m2
            vivo = False  # Solo se emite una vez

        id_año += 1

emisiones["geometry"] = df["geometry"]
emisiones["zona"] = df["zona"]
emisiones["parche"] = df["parche"]
emisiones["m2_punto"] = df["m2_punto"]

columnas_ordenadas = ["geometry", "zona", "parche", "m2_punto"] + años
emisiones = emisiones[columnas_ordenadas]

# %%
emisiones.to_csv("_emisiones_hojas_carbono.csv", index=False)

"""
EEEE M   M III  SSS  III  OOO  N   N      SSS  TTTTTT  OOO   CCC K  K
E    MM MM  I  S      I  O   O NN  N     S       TT   O   O C    K K
EEE  M M M  I   SSS   I  O   O N N N      SSS    TT   O   O C    KK
E    M   M  I      S  I  O   O N  NN         S   TT   O   O C    K K
EEEE M   M III SSSS  III  OOO  N   N     SSSS    TT    OOO   CCC K  K
"""
# %%
k = 0.18
S = 8.41 * 0.5  # Stock orgánico remineralizable
# Crear datos dummy
# datos = {
#     "2025": [500, 200, 10],
#     "2026": [400, 50, 5],
#     "2027": [300, 5,2 ]
# }
# df = pd.DataFrame(datos)
# df["m2_punto"] = [1, 1, 1]
# print(df)
# densidades = df[['2025', '2026', '2027']].astype(float)

densidades = df[años].astype(float)
m2 = df['m2_punto'].values.reshape(-1, 1)  # (n, 1) tantas filas como puntos y una columna
# %%
# Paso 1: detectar el primer año con densidad < 60
muertas = (densidades < 60).values  # (n, a)
idx_muerta = muertas.argmax(axis=1)  # (n,) indice a partir del cual la pradera muere
idx_muerta[~muertas.any(axis=1)] = 999  # Las que nunca mueren

# %%
# Paso 2: construir matriz t = (j - t0) para cada fila i, columna j
n, a = densidades.shape
t0 = idx_muerta.reshape(-1, 1)  # (n, 1) 
j = np.arange(a).reshape(1, -1)  # (1, a) cambio shape para poder restar

# Calcular t = j - t0 (años desde la desaparición)
t = j - t0  # (n, a)
# %%
# Enmascarar valores negativos (antes de la desaparición)
t = np.where(t >= 0, t, np.nan)
# %%
# Paso 3: aplicar la fórmula 
decay = S * (np.exp(-k * t) - np.exp(-k * (t + 1)))  # (n, a)
emisiones = decay * m2  # escalar por superficie (broadcast)

# emisiones_df = pd.DataFrame(emisiones, columns=['2025', '2026', '2027'], index=df.index) # para los datos dummy
emisiones_df = pd.DataFrame(emisiones, columns=años, index=df.index)
emisiones_df["geometry"] = df["geometry"]
emisiones_df["zona"] = df["zona"]
emisiones_df["parche"] = df["parche"]
emisiones_df["m2_punto"] = df["m2_punto"]

columnas_ordenadas = ["geometry", "zona", "parche", "m2_punto"] + años
emisiones_df = emisiones_df[columnas_ordenadas]

# %%
emisiones_df.to_csv("_emisiones_stock_carbono.csv", index=False)

# %%