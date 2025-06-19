#  %%
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

import geopandas as gpd
from shapely.geometry import mapping
from scipy.ndimage import binary_dilation
import rasterio
from rasterio.features import geometry_mask
import geopandas as gpd
from shapely.geometry import box

# === Parámetros ===
ruta_tif = "C:/Users/Julia/Downloads/DTMS/PNOA_MDT200_ETRS89_HU31_Barcelona.tif"
ruta_costa = "C:/Users/Julia/Documents/VSCODE/src/_ficheros_datos/coastline/LC/COSTA.shp"  # línea de costa real
altura_inundacion = 0.0  # metros
# ruta_costa = "C:/Users/Julia/Documents/VSCODE/src/_ficheros_datos/coastline/Spain_shapefile/es_1km.shp"

# %%
# === Abrir el DTM ===
with rasterio.open(ruta_tif) as src: #esto es un rasterio DatasetReader
    dtm = src.read(1) #esto es un ndarray
    transform = src.transform #esto es un affine.Affine
    nodata = src.nodata #esto es un float
    crs = src.crs
    bbox = box(*src.bounds)  # Bounding box de la imagen, es un polygon

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
# gdf_costa = gdf_costa[gdf_costa['BAJAMAR'] == True]
# Recortar a geometrías que intersectan con el raster
gdf_costa = gdf_costa[gdf_costa.intersects(bbox)]

# Filtrar por coordenada Y máxima
def max_y(geom):
    return max([pt[1] for pt in geom.coords]) if geom.type == 'LineString' else max(
        [max([pt[1] for pt in g.coords]) for g in geom.geoms])

gdf_costa = gdf_costa[gdf_costa.geometry.apply(max_y) <= 4.7e6]

gdf_costa.plot()
#%% Plot de las dos cosas
fig, ax = plt.subplots(figsize=(10, 8))
sc = ax.scatter(xs_valid, ys_valid, c=dtm_valid, cmap='terrain', s=1, alpha=0.8)
plt.colorbar(sc, ax=ax, label="Elevación (m)")
gdf_costa.plot(ax=ax, color='black', linewidth=1)
ax.set_title("DTM con línea de costa")
ax.set_xlabel("X (Easting)")
ax.set_ylabel("Y (Northing)")
plt.axis('equal')
plt.tight_layout()
plt.show()

# %%
# === Inicializar máscara vacía ===
mask_costa = np.zeros(dtm.shape, dtype=bool)
# %%
# === Iterar sobre cada línea ===
for i, geom in enumerate(gdf_costa.geometry):
    # Convertir a máscara binaria para esta línea
    mask_tmp = ~geometry_mask(
        [mapping(geom)],
        transform=transform,
        invert=True,
        out_shape=dtm.shape
    )
    # Acumular en la máscara final
    mask_costa |= mask_tmp
    n_true = np.sum(mask_costa)
    n_false = mask_costa.size - n_true
    print(f"[{i+1}/{len(gdf_costa)}] → mask_costa: True={n_true:,} | False={n_false:,}")
# %%
# === Crear figura ===
fig, ax = plt.subplots(figsize=(20,15), subplot_kw={'projection': ccrs.UTM(zone=31)})
ax.set_title("Píxeles que intersectan con la línea de costa", fontsize=14)

# === Pintar fondo (todo el DTM en gris claro) ===
# ax.imshow(
#     np.ma.masked_invalid(dtm),  # para evitar nodata
#     extent=extent,
#     transform=ccrs.UTM(zone=31),
#     origin='upper',
#     cmap='Greys',
#     alpha=0.5
# )

# === Pintar píxeles donde intersecta la costa (rojo) ===
ax.imshow(
    np.ma.masked_where(~mask_costa, mask_costa),
    extent=extent,
    transform=ccrs.UTM(zone=31),
    origin='upper',
    cmap='Reds',
    alpha=0.7
)

# === Dibujar la línea de costa por encima ===
ax.add_geometries(
    [linea],
    crs=ccrs.UTM(zone=31),
    facecolor='none',
    edgecolor='black',
    linewidth=1.2
)

# === Estética ===
ax.gridlines(draw_labels=True)
plt.show()

# %%
# === Crear máscara de celdas por debajo del nivel del mar ===
if nodata is not None:
    dtm = np.ma.masked_equal(dtm, nodata)

mask_bajo_agua = dtm < altura_inundacion

# === Simulación bathtub: dilatar desde la costa real ===
estructura = np.array([[1,1,1],[1,1,1],[1,1,1]])  # 8 conectividad
inundacion = binary_dilation(
    mask_costa,
    structure=estructura,
    iterations=500,
    mask=mask_bajo_agua
)

# === Visualización ===
fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.UTM(zone=31)})
ax.set_title(f"Inundación tipo Bathtub desde línea de costa (>{altura_inundacion} m)")

# Topografía base
img = ax.imshow(
    dtm,
    origin='upper',
    extent=extent,
    transform=ccrs.UTM(zone=31),
    cmap='terrain'
)

# Capa inundada
ax.imshow(
    np.ma.masked_where(~inundacion, inundacion),
    origin='upper',
    extent=extent,
    transform=ccrs.UTM(zone=31),
    cmap='Blues',
    alpha=0.5
)

# Línea de costa
ax.add_geometries(
    [linea],
    crs=ccrs.UTM(zone=31),
    facecolor='none',
    edgecolor='black',
    linewidth=1.2
)

# Estética
plt.colorbar(img, ax=ax, orientation='vertical', label='Altura (m)')
ax.gridlines(draw_labels=True)
plt.show()
# %%