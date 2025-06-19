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
haces_por_m  = 600
oc_por_haz = oc_secuestrado/ haces_por_m

años = [str(a) for a in range(2025, 2100)]

captura = df[años].copy()

for año in años:
    captura[año] = oc_por_haz * df["m2_punto"] * df[año]

# %%
captura["geometry"] = df["geometry"]
captura["zona"] = df["zona"]
captura["parche"] = df["parche"]
captura["m2_punto"] = df["m2_punto"]

columnas_ordenadas = ["geometry", "zona", "parche", "m2_punto"] + años
captura = captura[columnas_ordenadas]
# %%
captura.to_csv("_secuestro_carbono_densidad.csv", index=False)
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

# Calcular emisiones año a año
# Calcular la pérdida de densidad entre años consecutivos (delta)
densidad_anterior = df[años[:-1]].values
densidad_actual = df[años[1:]].values
delta_densidad = densidad_anterior - densidad_actual  # shape: (n_filas, n_años - 1)

# Escalar por m2 y factor de emisión
m2 = df['m2_punto'].values.reshape(-1, 1)
años_emisiones = años  # años completos, desde 2025

emisiones = delta_densidad *oc_por_haz * m2  # emisiones por m² en kg
# Insertar columna de emisiones = 0 para 2025 al inicio
emisiones = np.hstack([np.zeros((emisiones.shape[0], 1)), emisiones])

# Crear nuevo DataFrame con emisiones
df_emisiones = pd.DataFrame(emisiones, columns=años_emisiones)
df_emisiones["geometry"] = df["geometry"]
df_emisiones["zona"] = df["zona"]
df_emisiones["parche"] = df["parche"]
df_emisiones["m2_punto"] = df["m2_punto"]

# %%
df_emisiones.to_csv("_emisiones_hojas_carbono_densidad.csv", index=False)


# %%
