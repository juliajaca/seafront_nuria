#%%
import os
import pandas as pd
from unidecode import unidecode
import numpy as np
import re
import matplotlib.pyplot as plt

#  %%
cps =  pd.read_csv("C:/Users/Julia/Documents/VSCODE/src/_ficheros_datos/seguros/listado-codigos-postales-con-LatyLon.csv", sep=';')
cps['poblacion'] = cps['poblacion'].str.lower().apply(unidecode)
cps['provincia'] = cps['provincia'].str.lower()

# %%
dinero= pd.read_excel("C:/Users/Julia/Documents/VSCODE/src/_ficheros_datos/seguros/225-RREE Inun+Emb - Litoral 1996-2020.xlsx", skiprows=5, index_col='FECHA SINIESTRO')
#  %%
dinero['POBLACION'] = (dinero['POBLACION']).astype("string").str.lower().apply(unidecode)
dinero['MUNICIPIO'] = (dinero['MUNICIPIO']).str.lower().apply(unidecode)
dinero.loc[dinero['PROVINCIA'] == 'Balears, Illes', 'PROVINCIA'] ='Illes Balears'
dinero.loc[dinero['PROVINCIA'] == 'Palmas, Las', 'PROVINCIA'] ='Las Palmas'
dinero.loc[dinero['PROVINCIA'] == 'Coruña, A', 'PROVINCIA'] ='A Coruña'
dinero['PROVINCIA'] = dinero['PROVINCIA'].str.lower().apply(unidecode)
dinero = dinero.loc[dinero['CAUSA SINIESTRO'] == 'CAUSAS NATURALES/EMBATE DE MAR']
dinero['coste/capital ratio flag'] = 0
dinero.loc[dinero['COSTE TOTAL'] > dinero['CAPITAL ASEGURADO'], 'coste/capital ratio flag'] = 1
#  %%
# merged_left = dinero.reset_index().merge(cps.drop_duplicates(subset=['codigopostalid']), how="left", right_on="codigopostalid", left_on="CODIGO POSTAL").set_index(dinero.index.names)
# # %%
# duplicados = cps[cps.duplicated(['codigopostalid'], keep=False)]

# %%
dinero.groupby(['PROVINCIA']).size()
# %%
bal = dinero.loc[dinero['PROVINCIA'] == 'illes balears']
# %%
bal.groupby(['FECHA SINIESTRO']).size()
# %%
# Contar siniestros por día
df_diario = bal.resample("D").size().rename("siniestros")

# Agrupar por semana sumando los siniestros
df_semanal = df_diario.resample("W").sum()

# Encontrar la semana con más siniestros
semana_max = df_semanal.idxmax()  # Fecha de inicio de la semana con más siniestros
num_siniestros_max = df_semanal.max()  # Número máximo de siniestros en una semana
# Mostrar resultados
print(df_diario)  # Ver siniestros por día
print(df_semanal)  # Ver siniestros por semana
print(f"La semana con más siniestros empieza el {semana_max} y tuvo {num_siniestros_max} siniestros.")
# %%
# Crear gráficos
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# 📊 Siniestros diarios
axes[0].plot(df_diario.index, df_diario.values, marker="o", linestyle="-", color="b", label="Diario")
axes[0].set_title("Siniestros por Día")
axes[0].set_ylabel("Número de siniestros")
axes[0].legend()
axes[0].grid(True)

# 📈 Siniestros semanales
axes[1].plot(df_semanal.index, df_semanal.values, marker="s", linestyle="-", color="r", label="Semanal")
axes[1].set_title("Siniestros por Semana")
axes[1].set_ylabel("Número de siniestros")
axes[1].set_xlabel("Fecha")
axes[1].legend()
axes[1].grid(True)

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# SINIESTROS ESAS FECHAS
# %%
fechas = ['2001-11-10 00:00:00', '2001-11-11 00:00:00', '2001-11-13 00:00:00','2001-11-15 00:00:00','2001-11-16 00:00:00','2001-11-17 00:00:00','2001-11-23 00:00:00','2001-11-24 00:00:00']
drama = bal.loc[bal.index.isin(fechas)]
# %%
# Contar siniestros por cada categoría
# Contar siniestros por cada categoría y seleccionar los 10 más afectados
top_municipios = drama.groupby("MUNICIPIO").size().nlargest(10)
top_poblaciones = drama.groupby("POBLACION").size().nlargest(10)
top_cp = drama.groupby("CODIGO POSTAL").size().nlargest(10)

# Crear figura con 3 subgráficos
fig, axes = plt.subplots(3, 1, figsize=(10, 10))

# 📍 Siniestros por MUNICIPIO
top_municipios.plot(kind="bar", ax=axes[0], color="blue", edgecolor="black")
axes[0].set_title("Top 10 Municipios con Más Siniestros")
axes[0].set_ylabel("Número de Siniestros")
axes[0].set_xlabel("Municipio")
axes[0].tick_params(axis="x", rotation=30, labelsize=10)  # Reduce el tamaño de fuente

# 🏘️ Siniestros por POBLACIÓN
top_poblaciones.plot(kind="bar", ax=axes[1], color="green", edgecolor="black")
axes[1].set_title("Top 10 Poblaciones con Más Siniestros")
axes[1].set_ylabel("Número de Siniestros")
axes[1].set_xlabel("Población")
axes[1].tick_params(axis="x", rotation=30, labelsize=10)

# 📌 Siniestros por CÓDIGO POSTAL
top_cp.plot(kind="bar", ax=axes[2], color="red", edgecolor="black")
axes[2].set_title("Top 10 Códigos Postales con Más Siniestros")
axes[2].set_ylabel("Número de Siniestros")
axes[2].set_xlabel("Código Postal")
axes[2].tick_params(axis="x", rotation=30, labelsize=10)

# Ajustar el diseño
plt.tight_layout()
plt.show()
# %% AHORA BUSQUEDA POR GASTO
# Agrupar por semana y sumar los daños
diario_daños = bal.resample("D")["COSTE TOTAL"].sum()
semanal_daños = bal.resample("W")["COSTE TOTAL"].sum()

# Encontrar la semana con más daños
semana_max_daños = semanal_daños.idxmax()
max_daños = semanal_daños.max()

print(f"La semana con más daño económico fue la semana que comenzó el {semana_max_daños.strftime('%Y-%m-%d')}, con un total de {max_daños:,.2f} euros.")

# %%
# Crear las figuras
fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=False)

# Gráfico de daños por día
axes[0].plot(diario_daños.index, diario_daños.values, marker="o", linestyle="-", color="r")
axes[0].set_title("Daños Económicos por Día")
axes[0].set_ylabel("Daño en Euros")
axes[0].grid(True)

# Gráfico de daños por semana
axes[1].plot(semanal_daños.index, semanal_daños.values, marker="o", linestyle="-", color="b")
axes[1].set_title("Daños Económicos por Semana")
axes[1].set_ylabel("Daño en Euros")
axes[1].grid(True)

# Mejorar la visualización de fechas
plt.xticks(rotation=45)
plt.tight_layout()

# Mostrar el gráfico
plt.show()

# %% AHORA SEGUN LA ENERGIA MAXIMA DE LA OLA
data = pd.read_csv('C:/Users/Julia/Documents/VSCODE/src/siniestros_con_maximos.csv', sep= '\t', index_col=0, parse_dates=True)
# %%
data = data.loc[data['CAUSA SINIESTRO'] == 'CAUSAS NATURALES/EMBATE DE MAR']
data = data.loc[data['PROVINCIA'] == 'illes balears']
# %%
diario_daños = data.resample("D")["energia_max"].sum()
semanal_daños = data.resample("W")["energia_max"].sum()
print(semanal_daños.sort_values(ascending=False))

# Encontrar la semana con más daños
semana_max_daños = semanal_daños.idxmax()
max_daños = semanal_daños.max()

print(f"La semana con la ola más enérgica fue la semana que comenzó el {semana_max_daños.strftime('%Y-%m-%d')}, con un total de {max_daños:,.2f} energia maxima.")

# %%
# Crear las figuras
fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=False)
axes[0].plot(diario_daños.index, diario_daños.values, marker="o", linestyle="-", color="r")
axes[0].set_title("energia maxima por Día")
axes[0].set_ylabel("energia")
axes[0].grid(True)
axes[1].plot(semanal_daños.index, semanal_daños.values, marker="o", linestyle="-", color="b")
axes[1].set_title("Energia por Semana")
axes[1].set_ylabel("Energia")
axes[1].grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %% AHORA SEGUN LA ENERGIA MAXIMA DE LA OLA
diario_daños = data.resample("D")["potencia_max"].sum()
semanal_daños = data.resample("W")["potencia_max"].sum()
print(semanal_daños.sort_values(ascending=False))
semana_max_daños = semanal_daños.idxmax()
max_daños = semanal_daños.max()

print(f"La semana con la ola más potente fue la semana que comenzó el {semana_max_daños.strftime('%Y-%m-%d')}, con un total de {max_daños:,.2f} potencia maxima.")

# %%
fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=False)
axes[0].plot(diario_daños.index, diario_daños.values, marker="o", linestyle="-", color="r")
axes[0].set_title("potencia maxima por Día")
axes[0].set_ylabel("potencia")
axes[0].grid(True)
axes[1].plot(semanal_daños.index, semanal_daños.values, marker="o", linestyle="-", color="b")
axes[1].set_title("potencia por Semana")
axes[1].set_ylabel("potencia")
axes[1].grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %%
