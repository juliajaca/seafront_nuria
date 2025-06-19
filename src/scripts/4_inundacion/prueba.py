# %%
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from osgeo import gdal
import geopandas as gpd
from shapely.geometry import mapping
from scipy.ndimage import binary_dilation
import rasterio
from rasterio.features import geometry_mask
import geopandas as gpd

# %%
# Ruta al archivo GeoTIFF del DTM
ruta_tif = "C:/Users/Julia/Downloads/DTMS/PNOA_MDT200_ETRS89_HU31_Barcelona.tif"

# Abrimos el raster con rasterio
with rasterio.open(ruta_tif) as src:
    dtm = src.read(1)  # Leemos solo la primera banda
    transform = src.transform  # Matriz de transformación afín
    crs = src.crs  # Sistema de referencia espacial
    extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]

# %%

















































# %%
# Creamos la figura con Cartopy
fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.UTM(zone=31)})
ax.set_title("Modelo Digital del Terreno (DTM)", fontsize=14)

# Pintamos el DTM (con una máscara para valores nulos si es necesario)
masked_dtm = np.ma.masked_equal(dtm, src.nodata)

# Mostramos el raster usando imshow
img = ax.imshow(
    masked_dtm,
    origin='upper',
    extent=extent,
    transform=ccrs.UTM(zone=31),
    cmap='terrain'
)

# Añadimos barra de color y bordes
plt.colorbar(img, ax=ax, orientation='vertical', label='Altura (m)')
ax.coastlines(resolution='10m')
ax.gridlines(draw_labels=True)

plt.show()