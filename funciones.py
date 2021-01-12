import pandas as pd
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import os

def read_NCEP_txt(txts, resample = False, freq = '3H', npart = 11):
    '''Reads NCEP ascii partitioned files created with "run_extract_NCEP" function. This function reads partitioned data that has been already extracted.

        Parameters
            txts: list
                list of files to read
            resample: boolean
                True if resample method is requested, false if not (Optional). Default if False
            freq: string
                Optional, default is '3H'. It's necesary only if resample is True, this parameter defines the new time series time step. E.g. '3H' for 3 hours, '1D' for 1 day.
            npart: int
                Number of partitions to consider
        Return
            df2: dataframe
                times series of partitioned sea states.
        TODO
            Check wind direction, sometimes the values are negative.
    '''
    
    wave_vars   =['hs', 'tp', 'th', 'sp']
    cols        = ['Date', 'Time', 'Uabs', 'Udir', 'hs', 'tp', 'th', 'sp','np']
    cols        += [x + '_' + str(y) for y in range(1,npart + 1) for x in wave_vars]
    
    date_format = '%Y%m%d %H%M%S'
    parser      = lambda x: pd.datetime.strptime(x, date_format)
    
    #print('Reading NCEP files...')
    for txt in txts:
        if 'df' not in locals():
            df = pd.read_csv(txt, skiprows=1, header = None, names=cols, delim_whitespace=True, 
                             parse_dates = {'datetime': ['Date', 'Time']}, index_col = 'datetime')
        else:
            df = df.append(pd.read_csv(txt, skiprows=1, header = None, names=cols, delim_whitespace=True, 
                             parse_dates = {'datetime': ['Date', 'Time']}, index_col = 'datetime'))
                             
    df = df.sort_index()
    ## if there are duplicated indices, the resulting dataframe will have only the first one
    df = df[~df.index.duplicated(keep = 'first')]
    df = df[df.np >= 1]
    df.loc[df[df.np > 11].index, 'np'] = 11
    
    if resample == True:
        df2 = df.resample(rule = freq).first()
    else:
        df2 = df
    return df2
    
def download_era5(variables, years, area, outname, back_extension = False,
                 months = None, grid = 0.25, ts = 1, pathout = None):
    '''
        Function to dowload data from the era5 model of the ECMWF. To use this function you must have the key installed, if not go to the
        webpage: https://cds.climate.copernicus.eu/api-how-to.
        The cds API limit the number of items to download at once. If you one to download the 4 wave partitions and the wind components, it is recommended to download the wave partitions using the 0.5 grid and after that or at the same time on another box the wind components using the 0.25 deg. Unfortunately, the maximum items
        is exceeded trying to download the wave partitions and the wind components. There is data available from 1950 to now, but in two different datasets. Download requests must be split on 1979, e.g. if data for 1975-1982 is needed, one download should cover 1975 to 1978 and another should cover the period between 1979 to 1982.
        TODO: DELETE BACK_EXTENSION INPUT AND IMPLEMENT A WAY TO RECOGNIZE THE DATASET BASED ON THE REQUESTED YEARS. IT IS EASY BUT THE FUNCTION WILL BE TO LONG.
        Parameters
            variables: list of strings
                output of the get_era5_variables function
            years: list or int
                years in which the data will be extracted. If more than one year is requested, the list must be [initial year, final year]
            area: list
                [upper left corner latitude, upper left corner longitude, lower right latitude, lower right longitude]
            outname: str
                name of output file. WITHOUT EXTENSION!
            back_extension: boolean
                if True preliminary back enxtension data set will be used (data previous 1979) else regular dataset will be used.
            months: tuple. Default None
                months in which the data will be extracted. E.g. (1, 2) for jan and feb
            grid: float or None, default 0.25
                If you want to download data from the atmospheric model (wind components) you should use 0.25. You also can download data
                from the atmospheric model with a 0.5 degree resolution. If you want to download data from the oceanic model you should 
                use 0.5. You also can download the data using a 0.25 deg grid, but the wave data will be interpolated.
                As a last option you can download the data without specifing the grid but the data of the ocean model will be compressed
                in one quarter of the globe. Try not to use this option, but the functions to extract the data from the downloaded data
                can handle this.
            ts: int, default 1
                time step of the downloaded data. The data is available every hour.
            pathout: str
                path of the folder where the data will be saved
        Returns
            None
    '''
    area_str = str(area).replace(' ', '')
    hours = ['{}:00'.format(str(x).zfill(2)) for x in range(0, 24, ts)]
    days = [str(x).zfill(2) for x in range(32)]
    
    if months == None:
        months = np.arange(1, 13, 1)
    else:
        months = np.arange(months[0], months[1] + 1, 1)

    years_arr = np.arange(years[0], years[1] + 1, 1)

    ts_per_year = 365 * 24/ts
    years_per_download = int(120_000 / (ts_per_year * len(variables)))
    n_downloads = len(years_arr) / years_per_download
    if n_downloads.is_integer():
        n_downloads = int(n_downloads)
    else:
        n_downloads = int(n_downloads) + 1
        
    if back_extension == False:
        database = 'reanalysis-era5-single-levels'
    else:
        database = r'reanalysis-era5-single-levels-preliminary-back-extension'

    if len(years_arr) < years_per_download:
        with open('download0.py', 'w') as fout:
            fout.write("import cdsapi")
            fout.write("\nc = cdsapi.Client()")
            fout.write("\nc.retrieve(")
            fout.write("\n    '{}',".format(database))
            fout.write("\n    {")
            fout.write("\n        'variable':{},".format(str(variables)))
            fout.write("\n        'product_type':'reanalysis',")
            fout.write("\n        'year':{},".format([str(x) for x in years_arr]))
            fout.write("\n        'month':{},".format([str(x).zfill(2) for x in months]))
            fout.write("\n        'day':{},".format(days))
            fout.write("\n        'area': {},".format(area_str))
            if grid != None:
                fout.write("\n        'grid': [{},{}],".format(grid, grid))
            fout.write("\n        'time':{},".format(hours))
            fout.write("\n        'format':'netcdf'")
            fout.write("\n    },")
            fout.write("\n    '{}.nc')".format(outname))

        with open('{}.log'.format(outname), 'w') as log:
            log.write('year:\t{}\n'.format([str(x) for x in years_arr]))
            log.write('month:\t{}\n'.format([str(x).zfill(2) for x in months]))
            log.write('area:\t{}\n'.format(area))
            log.write('grid:\t{}\n'.format(grid))
            log.write('variables:\n')                      
            for var in variables:
                log.write('\t' + var + '\n')                    

        with open('bat_download.bat', 'w') as fbat:
            fbat.write('call activate PRDW\n')
            fbat.write('python download0.py\n')
            fbat.write('call deactivate')

        p = Popen('bat_download.bat', cwd = '.', shell = True)
        stdout, stderr = p.communicate()
        os.remove('bat_download.bat')
        os.remove('download0.py')

    else:

        with open('bat_download.bat', 'w') as fbat:
            fbat.write('call activate PRDW\n')
            
        with open('{}.log'.format(outname), 'w') as log:
            log.write('Download by parts:\n\n')

        start_years = years_arr[::years_per_download]
        end_years = [x - 1 for x in start_years[1:]]
        end_years.append(years[-1])

        for i in range(n_downloads):
            yi = start_years[i]
            yf = end_years[i]

            years_sub = np.arange(yi, yf + 1, 1)

            with open(f'download{i}.py', 'w') as fout:
                fout.write("import cdsapi")
                fout.write("\nc = cdsapi.Client()")
                fout.write("\nc.retrieve(")
                fout.write("\n    '{}',".format(database))
                fout.write("\n    {")
                fout.write("\n        'variable':{},".format(str(variables)))
                fout.write("\n        'product_type':'reanalysis',")
                fout.write("\n        'year':{},".format([str(x) for x in years_sub]))
                fout.write("\n        'month':{},".format([str(x).zfill(2) for x in months]))
                fout.write("\n        'day':{},".format(days))
                fout.write("\n        'area': {},".format(area_str))
                if grid != None:
                    fout.write("\n        'grid': [{},{}],".format(grid, grid))
                fout.write("\n        'time':{},".format(hours))
                fout.write("\n        'format':'netcdf'")
                fout.write("\n    },")
                fout.write("\n    '{}_part{}.nc')".format(outname, i))

            with open('{}.log'.format(outname), 'a') as log:
                log.write('part\t{}\n'.format(i))
                log.write('year:\t{}\n'.format([str(x) for x in years_sub]))
                log.write('month:\t{}\n'.format([str(x).zfill(2) for x in months]))
                log.write('area:\t{}\n'.format(area))
                log.write('grid:\t{}\n'.format(grid))
                log.write('variables:\n')                      
                for var in variables:
                    log.write('\t' + var + '\n')
                log.write('\n\n\n')
            
            with open('bat_download.bat', 'a') as fbat:
                fbat.write(f'python download{i}.py\n')
        
        with open('bat_download.bat', 'a') as fbat:
            fbat.write('call deactivate')

        p = Popen('bat_download.bat', cwd = '.', shell = True)
        stdout, stderr = p.communicate()    

        for i in range(n_downloads):
            os.remove(f'download{i}.py')
        os.remove('bat_download.bat')

    if pathout != None:
        for x in [x for x in os.listdir('.') if outname in x]:
            shutil.move(x, os.path.join(pathout, x))
            
            
def get_era5_variables(var):
    '''  THIS FUNCTION IS STILL IN DEVELOPMENT.
        Function to look for variables in the available variables of the era5 model. It is implemented using fuzzywuzzy. 
        Parameters
            requested_variables: str or list 
                The input has 3 optins which are described below
                    1) Input 'waves_partitions' if you want to download the data of the three swell partitions and the wind waves
                    2) Input 'wind_components' if you want to download the wind components of the atmospheric model.
                    3) Input a list with the strings to look for another variables
        Returns
            extracted_variables: list
                list of strings with the name of each one of the requested variables
    '''
    if var == 'waves_partitions':
        requested_variables = ['significant_wave_height_of_first_swell_partition',
                               'mean_wave_period_of_first_swell_partition',
                               'mean_wave_direction_of_first_swell_partition',
                               'significant_wave_height_of_second_swell_partition',
                               'mean_wave_period_of_second_swell_partition',
                               'mean_wave_direction_of_second_swell_partition',
                               'significant_wave_height_of_third_swell_partition',
                               'mean_wave_period_of_third_swell_partition',
                               'mean_wave_direction_of_third_swell_partition',
                               'significant_wave_height_of_wind_waves',
                               'mean_wave_period_of_wind_waves',
                               'mean_wave_direction_of_wind_waves']
    elif var == 'wind_components':
        requested_variables = ['10m_u_component_of_wind',
                               '10m_v_component_of_wind',
                               'mean_sea_level_pressure'
                               ]
    else:
        requested_variables
    
    df = pd.read_csv(Path(pyPRDW.__path__[0])/'__resources__'/'variables_era5.txt', header = None)
    variables_dummy = []
    for col in df.columns:
        variables_dummy.extend(list(df.loc[:, col]))
    variables = [x.split("'")[1] for x in variables_dummy if type(x) == str]
    extracted_variables = []
    for var in requested_variables:
        extracted_variables.append(process.extractOne(var, variables)[0])
    print('The variables which will be extracted area:\n')
    for ivar, var in enumerate(extracted_variables):
        print(str(ivar + 1) + ') ' + var)
    print('\nIf you are not happy, please be more specific with the input and execute the function again!')
    return extracted_variables

def plot_spectra(data, item = None, tstep = None, 
                 figsize = (8,8), cmap = 'viridis', cbar = False, cbar_label = None, 
                 levels = 'auto', ax = None, extend = 'both',
                 watermark = None, prdw_logo_path = None, 
                 prdw_logo_size = [0.69, 0.75, 0.15, 0.15], 
                 prdw_logo_alpha = 0.5, fig = None):
    
    ''' Polar spectra plot from a dataframe. By SK.
        ToDo: Fix cbar ticks when geometric progression is used on levels
        Parameters:
            data: dataframe or string
                If dataframe it must has the periods on index and directions on columns. String for plot timeste of a dfs2 file
            item: string, default None
                If data is string, you should specify the item name
            tstep:
                If data is string, you should specify the timestep to plot
            figsize: tuple
            cmap: string
            cbar: boolean (optional). Default: None
                True if you want to show the colorbar
            cbar_label: str (optional). Default: None
                label of the colorbar, bin units. It will work only if cbar == True.
            levels: array. Default: 'auto'
                If auto, levels are automatically calculated. Use np.geomspace(lmin, lmax, number) for levels following geometric progression.
            ax: matplotlib axis. Default = None, new axis created.
                Matplotlib axis to plot on defined as polar, it can be done using "subplot_kw = dict(projection = 'polar')".
            extend: string
                'both' for extend colorbar to min and max, 'min' or 'max'
            watermark: str (optional). Default None
                Displays watermark. Default: None 
            prdw_logo_path: str (optional). Defualt: None
                Complete path of the PRDW logo. It is stored on the gitlab documentation folder
            prdw_logo_size: list (optional). Default: [0.13, 0.61, 0.08, 0.08]
                [x0, y0, width, height]. The aspect of the logo is set to equal.
            prdw_logo_alpha: float (optional). Defaulut: 0.5
            fig: matplotlib figure
                You need to specify the matplotlib figure only if you are ploting this as a subplot and you want to used the prdw logo. Default = None, new figure created.
                
        Return
            ax: matplotlib axis
    '''
    if type(data) is not str:
        df = data
    else:
        dfs2in = Dfs.read(data)
        deltaf = dfs2in.i.values[1] - dfs2in.i.values[0]
        f = [dfs2in.i.values[0] + i * deltaf if deltaf < 1 else dfs2in.i.values[0] * deltaf**i for i in range(len(dfs2in.i.values))]
        df = pd.DataFrame(columns = dfs2in.j.values, index = [1/freq for freq in f], data = dfs2in[item].values[tstep,:,:])
        
    t = list(df.index)
    d = list(df.columns)
    v = df.values
#     return df
    
    ## wrapping the data
    d_ext = np.append(d,d[0]+360)
    X, Y = np.meshgrid(t, d_ext)
    v_extended = np.full([v.shape[0], v.shape[1] + 1], np.nan, dtype = v.dtype)
    v_extended[0:v.shape[0], 0:v.shape[1]] = v
    v_extended[0:v.shape[0], -1] = v_extended[0:v.shape[0], 0]
        
    cmap = plt.cm.get_cmap('viridis')
    cmap.set_under('whitesmoke')
    
    if ax == None:
        fig, ax = plt.subplots(figsize = figsize, subplot_kw = dict(projection = 'polar'))
    
    if levels == 'auto':
        dummy = ax.contourf(np.deg2rad(Y),X,v_extended.T, zorder=0, cmap = cmap, extend = extend)
    else:
        ## avoid probles with logNorm normalization
        v_extended[v_extended < levels[0]] = levels[0]/2
        dummy = ax.contourf(np.deg2rad(Y),X,v_extended.T, zorder=0, cmap = cmap, extend = extend, 
                        levels = levels, norm=mpl.colors.LogNorm(vmin = levels[0]), vmin = levels[0])

    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_yticklabels(['{}s'.format(x) for x in ax.get_yticks()])
    ax.tick_params(axis='y', colors='k')
    ax.tick_params(axis='x', colors='k')
    ax.grid(c = 'k')
    
    if cbar == False:
        pass
    else:
        cbar = plt.colorbar(dummy, fraction = 0.04, pad = 0.06, ticks = levels, format = mpl.ticker.LogFormatter())
        
        if cbar_label != None:
            cbar.set_label(cbar_label)
                         
    if watermark!= None:
        text = AnchoredText(watermark, 'upper right',frameon = False, borderpad = -2, prop=dict(fontsize = 'xx-small', alpha = 0.4)) ;
        ax.add_artist(text)
                         
    ## prdw logo
    if prdw_logo_path != None:
        im = plt.imread(prdw_logo_path)
        ax2 = fig.add_axes(prdw_logo_size)
        ax2.imshow(im, aspect = 'equal', alpha = prdw_logo_alpha)
        ax2.axis('off');
    
    return ax