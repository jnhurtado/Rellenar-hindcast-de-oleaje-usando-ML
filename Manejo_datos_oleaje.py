# -*- coding: utf-8 -*-
"""
Código de oleaje
"""

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
#import funciones
import os
import mikeio
from mikeio import Dfs0
from mikeio import Dfs2
from datetime import datetime
import pandas as pd
#import netCDF4 as nc
from osgeo import gdal # para usar grib



  

    
#dfs0 = Dfs0("NCEP_Spectra_from_Partitions_33.0S_72W_197901to200912_check.dfs0")
#dfs2 = Dfs2("NCEP_Spectra_from_Partitions_33.0S_72W_197901to200912.dfs2")
#ds = dfs0.read()
#df = ds.to_dataframe()


    
#ds =  xr.open_dataset("E:/Data/Wind_data_part0.nc")

names= [ "Wind_data_part0.nc"
        ,"Wind_data_part1.nc"
        ,"Wind_data_part2.nc"
        ,"Wind_data_part3.nc"
        ]

path = "E:/Data/"              #set location of the files

files = [path + name for name in names]

ds= xr.open_mfdataset(names)



def g_espectro(dataframe, variable, fecha_inicial, fecha_final):
    
    a = dataframe[variable][fecha_inicial:fecha_final]
    
    if str(variable)=="Hm0":
        tit= "Altura ola"; label="metros"
    elif str(variable) == "Tp":
        tit= "Periodo ola"; label="segundos"
    elif str(variable) == "Mean Dir":
        tit= "Dirección ola"; label="grados"
    elif str(variable) == "DSD":  
        tit= "Desviación estándar direccional"; label="grados"
        
    a.plot(xlabel="Tiempo", ylabel=label ,title= f"{tit}, Valparaíso 33S - 72W")
    



def g_viento(ds_variable, time, lat, lon):
    
    return ds_variable.isel(time=time).sel(latitude=lat,longitude=lon).plot()



#Ejemplo de uso


#g_espectro(df,"Hm0","2000-12-1","2001-12-2")
#df.index = (df.index - df.index[0]).total_seconds()

#plt.pause(1)
#g_viento(dswind, "m10", 2000, lat= -30, lon = -100, wd=260)

v10 = ds.v10
#v10.isel(time=100) para seleccionar un instante
#v10.sel(time=slice('1871-03','1871-11'),lon=slide(-70,-40),lat=slide(-50,-20))
#v10.sel(lat=-27.47, lon=153.03, method='nearest') toma la coordenada más cercana
#v10.sel(time=slice('1871-03','1871-11'),lon=slide(-70,-40),lat=slide(-50,-20)).plot()
#v10.mean(dim='time').plot(size=6)
#v10.sel(time=slice('1960-01',None)).mean(dim=('lat','lon')).plot()

#Máscaras
#v10_0 = ds.v10.isel(time=0)
#v10.where(v10_0 <5).where(v10_0 >2)


