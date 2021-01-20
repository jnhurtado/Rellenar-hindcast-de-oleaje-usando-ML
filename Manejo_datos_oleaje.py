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
from mikeio import Dfs2
from datetime import datetime
import pandas as pd
#import netCDF4 as nc
from osgeo import gdal # para usar grib
from scipy.fft import fft


  

    
dfs0 = Dfs0("NCEP_Spectra_from_Partitions_33.0S_72W_197901to200912_check.dfs0")
ds2 = Dfs2("NCEP_Spectra_from_Partitions_33.0S_72W_197901to200912.dfs2").read()
df = ds2.isel(0).isel(0).to_dataframe()


#intento
dfs2in = ds2
deltaf = dfs2in.index.values[1] - dfs2in.index.values[0]
f = [dfs2in.index.values[0] + i * deltaf if deltaf < 1 else dfs2in.i.values[0] * deltaf**i for i in range(len(dfs2in.i.values))]
df = pd.DataFrame(columns = dfs2in.j.values, index = [1/freq for freq in f], data = dfs2in[item].values[tstep,:,:])
   
    


names = ['Wind_data_part0.nc',
         'Wind_data_part1.nc',
         'Wind_data_part2.nc',
         'Wind_data_part3.1.nc',
         'Wind_data_part3.2.nc',]

#path = "E:/Data/"              #set location of the files

#files = [path + name for name in names]


ds1= xr.open_mfdataset(names)



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
    



def g_viento(dataserie, variable, time, lat, lon):
    
    return dataserie[variable].isel(time=time).sel(latitude=lat,longitude=lon).plot()



def cut_netcdf(new_file):
    #This function crop the netcdf file in two files and get rid of expver dimension
    #return two files without the expver dimension

    ds2 = xr.open_dataset(new_file)
    times = []
    
    for var in ds2:
        for t in reversed(range(ds2[var].shape[0])):
            if pd.isna(ds2[var].isel(time=t,expver=1))[0,0]:
                print(var," expvar format is 1 until time ",np.array(ds2["time"].isel(time=t)))
                times.append([var,t])
                break
        continue
    print(times)
    
    if times[0][1]==times[1][1]:
        
        rango1 = slice(None, str(np.array(ds2["time"].isel(time=times[0][1]))))
        rango5 = slice(str(np.array(ds2["time"].isel(time=times[0][1]+1))),None)
        
        ds2_era1 = ds2.isel(expver=0).sel(time=rango1).drop('expver',dim=None)
        ds2_era5 = ds2.isel(expver=1).sel(time=rango5).drop('expver',dim=None)
        
        ds2_era1.to_netcdf('cut_netcdf1.nc')
        ds2_era5.to_netcdf('cut_netcdf2.nc')
        
    else:
        return "Time changes of cordenate expvar are diferent for variable "+times

#Ejemplo de uso


g_espectro(df,"Hm0","2000-12-1","2001-12-2")
#df.index = (df.index - df.index[0]).total_seconds()

#plt.pause(1)
#g_viento(dswind, "m10", 2000, lat= -30, lon = -100, wd=260)


#v10.isel(time=100) para seleccionar un instante
#v10.sel(time=slice('1871-03','1871-11'),lon=slide(-70,-40),lat=slide(-50,-20))
#v10.sel(lat=-27.47, lon=153.03, method='nearest') toma la coordenada más cercana
#v10.sel(time=slice('1871-03','1871-11'),lon=slide(-70,-40),lat=slide(-50,-20)).plot()
#v10.mean(dim='time').plot(size=6)
#v10.sel(time=slice('1960-01',None)).mean(dim=('lat','lon')).plot()

#Máscaras
#v10_0 = ds.v10.isel(time=0)
#v10.where(v10_0 <5).where(v10_0 >2)


