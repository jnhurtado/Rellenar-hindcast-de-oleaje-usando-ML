def calc_tm01(df):
    aux0 = df.sum(axis = 1)
    dtheta = np.radians(df.columns[1]-df.columns[0])
    deltaf = (df.index[1]-df.index[0])
    m0 = aux0.sum(axis = 0)*dtheta*deltaf
    m1 = np.sum(np.multiply(aux0.values, aux0.index.values))*dtheta*deltaf
    tm01 = m0/m1
    
    return tm01
    
def calc_dp(df):
    dp = df.max(axis = 0).idxmax()
    
    return dp
    
def calc_dm(df):
    aux = df.sum(axis = 0)
    num = np.sum(np.multiply(aux.values, np.sin(np.radians(aux.index.values))))
    den = np.sum(np.multiply(aux.values, np.cos(np.radians(aux.index.values))))
    dm = np.mod(np.degrees(np.arctan2(num, den)), 360)
    
    return dm