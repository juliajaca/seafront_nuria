#  %%
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from rasterio.features import rasterize
import geopandas as gpd
from shapely.geometry import mapping
from scipy.ndimage import binary_dilation
import rasterio
from rasterio.features import geometry_mask
import geopandas as gpd
from shapely.geometry import box

# === Parámetros ===
# ruta_tif = "C:/Users/Julia/Downloads/DTMS/PNOA_MDT200_ETRS89_HU31_Barcelona.tif"
ruta_tif= "C:/Users/Julia/Nextcloud/seafront nuria/DTMS_5m/Girona_tifs/PNOA_MDT05_ETRS89_HU30_0221_LID.tif"
ruta_costa = "C:/Users/Julia/Documents/VSCODE/src/_ficheros_datos/coastline/LC/COSTA.shp"  # línea de costa real
# altura_inundacion = 0.5  # metros
# ruta_costa = "C:/Users/Julia/Documents/VSCODE/src/_ficheros_datos/coastline/Spain_shapefile/es_1km.shp"

# %%
# === Abrir el DTM ===
with rasterio.open(ruta_tif) as src: #esto es un rasterio DatasetReader
    dtm = src.read(1) #esto es un ndarray
    transform = src.transform #esto es un affine.Affine
    nodata = src.nodata #esto es un float
    crs = src.crs
    out_shape= dtm.shape
    bbox = box(*src.bounds)  # Bounding box de la imagen, es un polygon
    extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
# %%
# # Si no está definido en el archivo, lo pones tú manualmente
# if nodata is None:
#     nodata = -32767  # valor típico
# # Enmascarar nodata

dtm[dtm < 0] = 0

valores_unicos, conteos = np.unique(dtm, return_counts=True)
# Mostrar valores y su frecuencia
for val, cnt in zip(valores_unicos, conteos):
    print(f"Valor: {val}, Frecuencia: {cnt}")

valores_filtrados = dtm[(dtm > 0) & (dtm <= 1)]
plt.hist(valores_filtrados.flatten(), bins=60, edgecolor='black')  
plt.title("Histograma de frecuencias")
plt.xlabel("Valor")
plt.ylabel("Frecuencia")
plt.show()


elevacion_masked = np.ma.masked_equal(dtm, nodata)
# %%
# === Crear grilla de coordenadas X, Y ===
rows, cols = dtm.shape
row_idx, col_idx = np.meshgrid(np.arange(rows), np.arange(cols), indexing='ij')
xs, ys = rasterio.transform.xy(transform, row_idx, col_idx)

# Convertir a arrays planos para scatter
xs = np.array(xs).flatten()
ys = np.array(ys).flatten()
dtm_flat = dtm.flatten()

# Eliminar nodata
valid_mask = (dtm_flat != nodata) if nodata is not None else ~np.isnan(dtm_flat)
xs_valid = xs[valid_mask]
ys_valid = ys[valid_mask]
dtm_valid = dtm_flat[valid_mask]

# === Cargar y preparar la línea de costa ===
gdf_costa = gpd.read_file(ruta_costa).to_crs(crs.to_string())
# Filtrar solo las que tienen BAJAMAR == True
gdf_costa = gdf_costa[gdf_costa['BAJAMAR'] == True]
# Recortar a geometrías que intersectan con el raster
gdf_costa = gdf_costa[gdf_costa.intersects(bbox)]

# Filtrar por coordenada Y máxima
def max_y(geom):
    return max([pt[1] for pt in geom.coords]) if geom.type == 'LineString' else max(
        [max([pt[1] for pt in g.coords]) for g in geom.geoms])

# gdf_costa = gdf_costa[gdf_costa.geometry.apply(max_y) <= 4.7e6]

gdf_costa.plot()

#%% Plot de las dos cosas
# fig, ax = plt.subplots(figsize=(10, 8))
# sc = ax.scatter(xs_valid, ys_valid, c=dtm_valid, cmap='terrain', s=1, alpha=0.8)
# plt.colorbar(sc, ax=ax, label="Elevación (m)")
# gdf_costa.plot(ax=ax, color='black', linewidth=1)
# ax.set_title("DTM con línea de costa")
# ax.set_xlabel("X (Easting)")
# ax.set_ylabel("Y (Northing)")
# plt.axis('equal')
# plt.tight_layout()
# plt.show()

# %% plot con imshow
# Mostrar el ráster
plt.imshow(elevacion_masked, cmap="terrain", extent=extent)
plt.colorbar(label="Elevación (m)")
plt.title("Modelo de Elevación del Terreno")
plt.xlabel("Longitud")
plt.ylabel("Latitud")
plt.show()
# %% solapamiento linea costa- pixeles mapa
#=== Rasterizar la línea de costa (valor 1 donde intersecta) ===
mask_costa = rasterize(
    [(geom, 1) for geom in gdf_costa.geometry], # Geometrías a pintar, Le dice a rasterize: "dibuja esta geometría, y donde caiga, pon un 1"
    out_shape=out_shape,  # Tamaño de la imagen (igual que tu raster), forma el array de destino
    transform=transform, # Donde está cada píxel (la georreferenciación). Le dice: "este píxel (fila, columna) está en tal lugar del mundo". Es como la “regla” para mapear coordenadas reales a píxeles.
    fill=0, # Qué valor poner donde NO hay línea
    dtype='uint8'  # Tipo de dato (número entero pequeño)
)

# === Resultado: máscara booleana (True = costa) ===
mask_bool = mask_costa.astype(bool)

# Opcional: visualización rápida
plt.imshow(mask_bool, cmap='Reds')
plt.title("Píxeles intersectados por línea de costa")
plt.show()


# %% BATHUB
# === PARÁMETROS ===
print("mask_costa: True =", np.count_nonzero(mask_costa))
altura_ola = 1  # metros

# 1. Crear máscara de zonas más bajas que el nivel del agua
nivel_mar = dtm < altura_ola
print("nivel_mar: True =", np.count_nonzero(nivel_mar))

# Máscara para evitar propagación hacia mar 
umbral_altura_minima = 0.001  # ajusta este valor según tu caso
mask_valida = dtm > umbral_altura_minima
print("mask_valida (elevación > 0.01): True =", np.count_nonzero(mask_valida))

# # 2. Crear una máscara vacía de inundación
inundado = mask_costa & nivel_mar
print("Píxeles iniciales de inundación:", np.count_nonzero(inundado))

# %%
inundado_masked = np.ma.masked_where(inundado == 0, inundado)
plt.figure(figsize=(10, 8))

plt.imshow(inundado_masked, cmap="Reds", extent=extent)
plt.title("Zonas de partida de la inundación (costa + bajo nivel mar)")
plt.xlabel("Longitud")
plt.ylabel("Latitud")
plt.axis("equal")
plt.tight_layout()
plt.colorbar(label="Inundado (1=True)")
plt.show()
# %%
# 4. Propagar la inundación iterativamente (bañera) Mientras haya más píxeles nuevos que podemos inundar
while True:
    num_ceros = np.count_nonzero(inundado == 0) # es lo mismo que num_ceros = np.sum(~inundado.mask) 
    print("Número de ceros:", num_ceros)
    inundado_nuevo = binary_dilation(inundado) & nivel_mar & mask_valida
    # if np.array_equal(inundado_nuevo, inundado):
    #     break
    if not np.any(inundado_nuevo != inundado):
        break
    inundado = inundado_nuevo
# %%
plt.figure(figsize=(10, 8))
plt.imshow(elevacion_masked, cmap='terrain',alpha= 0.5)
plt.imshow(np.ma.masked_where(~inundado, inundado), cmap='Reds', alpha=1,  vmin=0, vmax=altura_ola,)
plt.title(f"Inundación tipo Bathtub desde la costa (nivel mar {altura_ola} m)")
plt.colorbar(label="Elevación (m)")
plt.show()
# %%
