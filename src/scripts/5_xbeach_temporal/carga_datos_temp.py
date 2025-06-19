# %%

import scipy
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
# lectura netcdfs
from netCDF4 import Dataset, stringtochar
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.io import loadmat
# %%
file_path = 'C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/5_xbeach_temporal/datos/med_reference_hrgrid_summary.mat'
medias = scipy.io.loadmat(file_path)
m = medias['TPRESREF']
valores_no_nan = m[~np.isnan(m)]
lat = medias['LATMOD']
lon = medias['LONMOD']
m = m[:,:,0,6] # las temperaturas de julio superficiales, en m hay 25019 nans
# %%
tendencias = scipy.io.loadmat('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/5_xbeach_temporal/datos/med_projections_rcp85_hrgrid_summary.mat')
t= tendencias['TANOMJUL'] # hay 24120 nans
lat2 = tendencias['LATMOD']
lon2 = tendencias['LONMOD']

profundidades = {
    'Profundidad 0 (superficie)': 0, 
    'Profundidad 42 (más profunda)': 41
}

for titulo, idx in profundidades.items():
    plt.figure(figsize=(10, 6))
    plt.imshow(t[:, :, idx], origin='lower', cmap='viridis', aspect='auto')
    plt.title(f'Temperatura del mar - {titulo}')
    plt.colorbar(label='°C')
    plt.xlabel('Longitud')
    plt.ylabel('Latitud')
    plt.tight_layout()
    plt.show()

t = tendencias['TANOMJUL'][:,:, 0] #uso la temperatura superficial
valores_no_nan_t = t[~np.isnan(t)]
# %%
print(np.array_equal(lat,lat2)) #son iguales
# %%
"""
 ____  _      ____  _      ____  _     _  ____  ____
/  _ \/ \  /|/  _ \/ \__/|/  _ \/ \   / \/  _ \/ ___\
| / \|| |\ ||| / \|| |\/||| / \|| |   | || / \||    \
| |-||| | \||| \_/|| |  ||| |-||| |_/\| || |-||\___ |
\_/ \|\_/  \|\____/\_/  \|\_/ \|\____/\_/\_/ \|\____/

"""
variacion_interanual = pd.read_csv('C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/SST_AR4_timeseries_Balear.dat', sep='\s+', header=None, skiprows=1)
a = variacion_interanual.iloc[:, [0, 1]]
# %% 1 calcular las anomalias
# Variables para regresión
X = a[0].values.reshape(-1, 1)
y = a[1].values
# Ajuste
modelo = LinearRegression()
modelo.fit(X, y)
a['ajuste'] = modelo.predict(X)

''' Con polyfit de numpy es mas
# Ajuste lineal de primer grado (recta)
coef = np.polyfit(df['año'], df['temperatura'], deg=1)  # coef[0] = pendiente, coef[1] = intercepto

# Evaluar la recta ajustada para todos los años
df['ajuste'] = np.polyval(coef, df['año'])
# Anomalía = temperatura observada - temperatura esperada por la recta
df['anomalia'] = df['temperatura'] - df['ajuste']
'''

# Predicción para cada añoaf['ajuste'] = modelo.predict(X)
a['anomalia'] = a[1] - a['ajuste']
df_anomalias = a[a[0] >= 2010][[0, 'anomalia']]

# %%
# PRUEBA CON PLAYA
# %%
lat_playa = 41.19729861
lon_playa = 1.656871964

# Calcular el índice de latitud más cercano
idx_lat = np.abs(lat[0,:] - lat_playa).argmin()

# Calcular el índice de longitud más cercano
idx_lon = np.abs(lon[:,0] - lon_playa).argmin()

print(f"Índice latitud: {idx_lat}, valor: {lat[0,:][idx_lat]}")
print(f"Índice longitud: {idx_lon}, valor: {lon[:,0][idx_lon]}")
print(f"M, valor: {m[idx_lat, idx_lon]}")
print(f"T, valor: {t[idx_lat, idx_lon]}")
# %%

def devolver_sst(lat_playa, lon_playa, año):
    idx_lat = np.abs(lat[0,:] - lat_playa).argmin()

    # Calcular el índice de longitud más cercano
    idx_lon = np.abs(lon[:,0] - lon_playa).argmin()

    print(f"Índice latitud: {idx_lat}, valor: {lat[0,:][idx_lat]}")
    print(f"Índice longitud: {idx_lon}, valor: {lon[:,0][idx_lon]}")
    print(f"M, valor: {m[idx_lat, idx_lon]}")
    print(f"T, valor: {t[idx_lat, idx_lon]}")

    m_playa = m[idx_lat, idx_lon]
    t_playa = t[idx_lat, idx_lon]
    anomalia  = df_anomalias.loc[df_anomalias.iloc[:, 0] == año]['anomalia'].values
    temperatura = m_playa  + t_playa / 100 * (año-1995) + anomalia
    print(f"La temperatura es : {temperatura}")
    return temperatura[0]

temp = devolver_sst(41.19, 1.66, 2020 )

# temp = devolver_sst(38.861053, 0.03409245, 2020 )
# %%
# lat_grid, lon_grid = np.meshgrid(lat, lon, indexing='ij')  # shape (334, 120)

# Mascara de puntos válidos (no NaN a profundidad 0)

# %%
def devolver_sst2(lat_playa, lon_playa, año):
    # print(f"La posicion de mi playa es: lat={lat_playa}, lon={lon_playa}, ano {año}")
    validos = ~np.isnan(m[:, :])
    validos_t = ~np.isnan(t[:, :])

    # Calcular la distancia cuadrada (más rápido que la distancia real para comparar)
    dist_sq = (lat - lat_playa)**2 + (lon - lon_playa)**2

    # Poner distancia infinita donde hay NaNs para que no se seleccionen
    dist_sq[~validos] = np.inf

    # Buscar el índice del mínimo
    idx_lon_m, idx_lat_m = np.unravel_index(np.argmin(dist_sq), dist_sq.shape)
    dist_sq[~validos_t] = np.inf
    idx_lon_t, idx_lat_t = np.unravel_index(np.argmin(dist_sq), dist_sq.shape)
    # print(f"Los idx son=lon m: {idx_lon_m}, lat_m ={idx_lat_m}, lon t: {idx_lon_t}, lat t: {idx_lat_t}")

    # print(f"Punto más cercano válido: lat={lat[0,:][idx_lat_m]}, lon={lon[:,0][idx_lon_m]}")
    # print(f"Punto más cercano válido: lat={lat[0,:][idx_lat_t]}, lon={lon[:,0][idx_lon_t]}")

    # print(f"Punto más cercano válido: lat={lat[0,:][idx_lat]}, lon={lon[:,0][idx_lon]}")
    # print(f'Lon indices son lat=  {idx_lat} y lon = {idx_lon}')
    # print(f"Temperatura en superficie allí: {m[idx_lon, idx_lat]:.2f} °C")
    m_playa = m[idx_lon_m, idx_lat_m]
    t_playa = t[idx_lon_t, idx_lat_t]
    # print(f"Temdendia es: {t_playa}")

    anomalia  = df_anomalias.loc[df_anomalias.iloc[:, 0] == año]['anomalia'].values[0]
    temperatura = m_playa  + t_playa / 100 * (año-1995) + anomalia
    # print(f'la anomalia es {anomalia}, la m es {m_playa}, la tendendia es { t_playa / 100 * (año-1995)}')
    # print(f"La temperatura es : {temperatura}")
    return temperatura

# temp = devolver_sst2(41.19, 1.66, 2020 )
temp = devolver_sst2(37.87408266, -0.754072706, 2020)
temp = devolver_sst2(37.87408266, -0.754072706, 2030)
temp = devolver_sst2(37.87408266, -0.754072706, 2040)
temp = devolver_sst2(37.87408266, -0.754072706, 2050)
temp = devolver_sst2(37.87408266, -0.754072706, 2060)
temp = devolver_sst2(37.87408266, -0.754072706, 2070)
temp = devolver_sst2(37.87408266, -0.754072706, 2080)
temp = devolver_sst2(37.87408266, -0.754072706, 2090)


# TEMERATURAS DE COPERNICUS

# %% COMPROBACION
path= 'C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/5_xbeach_temporal/datos/med-cmcc-tem-rean-m_1750340953072_temperatura_med1985-2022.nc' 

dataset = Dataset(path, "r")
# %%
print("\n🔹 Dimensiones:")
for var_name in dataset.dimensions:
    print(f"\nDimension: {var_name}")
# %%
vars_nc = {}
print("\n🔹 Atributos de las Variables:")
for var_name in dataset.variables:
    var = dataset.variables[var_name]  # <- accede al objeto variable
    print(f"\nVariable: {var_name}")
    print(f"  Dimensiones: {var.dimensions}")
    print(f"  Shape: {var.shape}")
    print(f" Tipo de dato: {dataset.variables[var_name].dtype}")
    vars_nc[var_name] = dataset.variables[var_name][:]
    for attr in var.ncattrs():
        print(f"  {attr}: {var.getncattr(attr)}")
# %%
print("\n🔹 Atributos Globales:")
for attr in dataset.ncattrs():
    print(f"{attr}: {dataset.getncattr(attr)}")

# %%
for variable, valor in vars_nc.items():
    print(variable, ' tiene ' ,len(valor), ' valores')
    print(valor[0:10])
    print(valor.shape)
    print('--------------')
# %%
# La variable se llama 'thetao' 
temp = dataset.variables['thetao'][:]  # shape: (432, 1, 203, 264)

# Selecciona solo la capa de superficie (profundidad 0)
temp = temp[:, 0, :, :]  # shape: (432, 203, 264)

# Selecciona los índices correspondientes a julio
# Como hay 12 meses por año, julio es el mes 7, o índice 6 (0-based), cada 12 pasos:
julio_indices = np.arange(6, temp.shape[0], 12)  # índices de julio en la dimensión temporal

# Extrae y promedia sobre esos meses de julio
temp_julio = temp[julio_indices, :, :]  # shape: (36, 203, 264)
media_julio = np.nanmean(temp_julio, axis=0)  # shape: (203, 264)

# Ahora media_julio contiene la temperatura media de julio (1987–2022)
print("Media de julio calculada. :", media_julio)
# %%
media_julio2 = np.nanmean(temp_julio) 
# %%
