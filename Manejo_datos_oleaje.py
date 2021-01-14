# -*- coding: utf-8 -*-
"""
Código de oleaje
"""


import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
import funciones
import os
import mikeio
from mikeio import Dfs0
from datetime import datetime
import pandas as pd
import netCDF4 as nc
from osgeo import gdal # para usar grib



  
def dataframe_NCEP(archivo):
    
    dfs0 = Dfs0(f"/Users/56993/Desktop/Data/Waves/{archivo}")
    ds = dfs0.read()
    df = ds.to_dataframe()
    return df

def dataserie_netcdf(archivo):
    
    ds = nc.Dataset(f"/Users/56993/Desktop/Data/Wind/{archivo}")
    print("Dimensión de los parametros de la serie")
    for dim in ds.dimensions.values():
        print(dim)  
    return ds






def g_espectro(dataframe, variable, fecha_inicial, fecha_final):
    
    a = dataframe[variable][fecha_inicial:fecha_final]
    
    if variable=="Hm0":
        tit= "Altura ola"; label="metros"
    elif variable == "Tp":
        tit= "Periodo ola"; label="segundos"
    elif variable == "Mean Dir":
        tit= "Dirección ola"; label="grados"
    elif variable == "DSD":  
        tit= "Desviación estándar direccional"; label="grados"
        
    a.plot(xlabel="Tiempo", ylabel=label ,title= f"{tit}, Valparaíso 33S - 72W")
    



def g_viento(dataserie, variable, fecha):
    
    if variable == "magnitud":
        u = np.array(dataserie["u10"][fecha,0,:,:])
        v = np.array(dataserie["v10"][fecha,0,:,:])
        np.sqrt(np.multiply(u,v))
        
    a = np.array(dataserie[variable][fecha,0,:,:])
    
    if variable=="u10":
        tit= "Viento en dirección x"; label="m/s"
    elif variable == "v10":
        tit= "Viento en dirección y"; label="m/s"
    elif variable == "magnitud":
        tit= "Magnitud iento"; label="m/s"
    elif variable == "sp":
        tit= "Presión aire superficial"; label="Pa"
        
    plt.xlabel="Tiempo"
    plt.ylabel=label
    plt.title= f"{tit}, Valparaíso 33S - 72W"
    plt.imshow(a,cmap="RdYlBu")
    return plt.show()





#Ejemplo de uso

df_wave = dataframe_NCEP("NCEP_Spectra_from_Partitions_33.0S_72W_197901to200912_check.dfs0")
g_espectro(df_wave,"Hm0","2000-12-1","2001-12-2")
#df.index = (df.index - df.index[0]).total_seconds()

plt.pause(1)
ds_wind = dataserie_netcdf("Wind_1979-2020.nc")
g_viento(ds_wind, "v10", 2000)









