# %%
import xarray as xr
import numpy as np
data = xr.DataArray(np.random.randn(2, 3), dims=("x", "y"), coords={"x": [10, 20]})

# %%
#  para generar el archivo requirements
# pip freeze > requirements.txt