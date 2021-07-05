import numpy as np
    
    

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
    md = []
    tm01 = []
    dsd = []
    Dp = []
    
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
        
        
        '''Peak period'''
        
        tpi=dfi.max(axis=0)
        tpi=1/tpi.idxmax()
        tp.append(tpi)
        
        '''Peak Direction'''

        Dpi=dfi.T.max(axis=0)
        Dpi=Dpi.idxmax()
        Dp.append(Dpi)
        

        if units == 'rad':
            
            '''Mean direction'''
            
            aux = dfi.T.sum(axis = 0)
            num = np.sum(np.multiply(aux.values, np.sin(np.radians(dfi.index))))
            den = np.sum(np.multiply(aux.values, np.cos(np.radians(dfi.index))))
            md.append(np.mod(np.degrees(np.arctan2(num, den)), 360))
            
            '''Mean period'''
            
            aux0 = dfi.T.sum(axis = 1)
            dtheta = np.radians(dfi.columns[1]-dfi.columns[0])
            deltaf = (dfi.index[1]-dfi.index[0])
            m0 = aux0.sum(axis = 0)*dtheta*deltaf
            m1 = np.sum(np.multiply(aux0.values, aux0.index))*dtheta*deltaf
            tm01.append( m0/m1)
            
            '''Directional Standard Deviation'''
                    
            dtheta = np.radians(dfi.columns[1]-dfi.columns[0])
            deltaf = (dfi.index[1]-dfi.index[0])
            aux = dfi.T.sum(axis = 0)
            m0 = aux.sum(axis = 0)*dtheta*deltaf
            b = np.sum(np.multiply(aux.values, np.sin(np.radians(dfi.index))))/m0*dtheta*deltaf
            a = np.sum(np.multiply(aux.values, np.cos(np.radians(dfi.index))))/m0*dtheta*deltaf
            dsd.append(np.mod(np.degrees((2*(1-(a**2 + b**2)**0.5))**0.5),360))
            
            
        
    if len(hm0) > 1:
        return hm0, tp, md, tm01, dsd, Dp
    else:
        return hm0[0], tp[0], md[0], tm[0] , dsd[0], Dp[0]
        
