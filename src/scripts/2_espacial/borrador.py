# %%
import math
import geopandas as gpd
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import Point
import numpy as np
import matplotlib.pyplot as plt
# %matplotlib widget
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString
from scipy.interpolate import griddata
import math
import matplotlib.ticker as mticker
# ------- 
# %%
# -------
# POSIDONIA
# -------
posidonia = gpd.read_file("C:/Users/Julia/Documents/VSCODE_SEAFRONT_NURIA/src/scripts/2_espacial/datos/areas_praderas_PeninsulaBaleares/posidonia_filtrada/output_filtrado.shp")
islas = ['Mallorca', 'Menorca', 'Ibiza', ]
posi_bal = posidonia.loc[posidonia['Prov_Isla'].isin(islas)].reset_index(drop=True)
# %%