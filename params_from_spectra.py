import numpy as np
import pandas as pd

def params_from_spectra(datain, item = None, units = None):
    ''' Compute hm0 & tp from spectra

        Parameters
            datain: str, list, dataframe
                if str it must be the complete path of a dfs2 file. If dataframe or list of dataframes, the index must be the directions, and columns the frequencies.
            item: string, Default None
                dfs2 item to compute wave parameters, it is used only if datain is str
            units: string, Default None
                If data in not str, you must specify the units of the spectra, either `rad`if it is in m^2/s/rad or `deg` if m^2/s/deg. If datain dfs2 the units are an attribute of the dataset
        Returns
            hm0, tp: tuple
                list or float withy hm0, tp values
    '''
    ## read input dfs2, this file must has 1 item.
    
    if type(datain) is str:
        dfs2in = Dfs.read(datain)
        df = dfs2in.i.values[1] - dfs2in.i.values[0]
        f = [dfs2in.i.values[0] + i * df if df < 1 else dfs2in.i.values[0] * df**i for i in range(len(dfs2in.i.values))]
        listin = [pd.DataFrame(columns = dfs2in.j.values, index = f, data = dfs2in[[x for x in dfs2in.keys()][0]].values[t,:,:]).T for t in range(len(dfs2in.Timestep.values))]
        units = dfs2in[item].unit.split('/')[-1]
    
    elif type(datain) is list:
        listin = datain
    
    else:
        listin = [datain]
    print(type(datain))
    
    df = listin
    
    hm0 = []
    tp = []
    
        
    for dfi in df:
        ## check if geometric progression or constant frequency spacing is used
        if dfi.columns[1] - dfi.columns[0] == dfi.columns[2] - dfi.columns[1]:
            dfreq = dfi.columns[1] - dfi.columns[0]
        else:
            dfreq = dfi.columns[1]/dfi.columns[0]
        
        ## only constant direction sp
        dtheta = np.abs(dfi.index[1] - dfi.index[0])

        if units == 'rad':     
            serie1 = dfi.sum(axis = 0) * np.deg2rad(dtheta)
        elif units == 'deg':  
            serie1 = dfi.sum(axis = 0) * dtheta
        
        else:
            print('You must specify the units of the spectra, either `rad`if it is in m^2/s/rad or `deg` if m^2/s/deg')
            return None
            
        factor = (dfreq - 1.0 / dfreq)/2
        
        serie2 = serie1 * serie1.index * factor
        hm0.append(4 * np.sqrt(serie2.sum()))
        
        tpi=dfi.max(axis=0)
        tpi=1/tpi.idxmax()
        tp.append(tpi)
        
    if len(hm0) > 1:
        return hm0, tp
    else:
        return hm0[0], tp[0]
        
