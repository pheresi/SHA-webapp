#!/usr/bin/env python3

# import sys
import numpy as np
import json
import csv
import os
from pandas import notnull
from scipy import interpolate
#from pathlib import Path
#from nose.tools import set_trace

# Periods for UHS
T_UHS_ALL = {'TestIM':(1,2,3),
             'FIV3':(0.1,0.5,1,1.5,2,2.5,3), 
             'SA':(0,0.1,0.3,0.5,0.8,1.0,1.3,1.5,1.8,2,2.5,3,3.5,4,4.5,5),
             'SAAVG':(0.1,0.5,1,1.5,2,2.5,3)}

T_available_ALL = {'FIV3': np.arange(1, 31)/10, 
             'SA': np.arange(0, 51)/10,
             'SAAVG': np.arange(1, 31)/10}

def computeHazardCurve(dataInput):
    '''
        Interpolates the hazard curve at a specific site
    '''
    Lat = float(dataInput['Lat'])
    Lon = float(dataInput['Lon'])
    threshold = float(dataInput['threshold'])      # Threshold in °
    IMname = dataInput['IM']
    T_HC = float(dataInput['T'])
    soil = dataInput['soil']
    
    # Check if IM is supported and get T_available
    try:
        T_available = T_available_ALL[IMname]
    except KeyError:
        raise KeyError("IM not supported: " + IMname)

    # Check if T_HC is in the range of T_available
    if T_HC < min(T_available) or T_HC > max(T_available):
        raise Exception("Period out of bounds for this IM")
        
    # If T_HC is exactly one of the T_available, get the curve directly    
    if T_HC in T_available:
        IM_HC, MAF_HC = getHazardCurveAtSite(IMname, soil, T_HC, Lat, Lon, 
                                             threshold)
    else: # If not, we interpolate between periods
        T_upper = T_available[T_available >= T_HC].min()
        IM_HC_upper, MAF_HC_upper = getHazardCurveAtSite(IMname, soil, T_upper, 
                                                         Lat, Lon, threshold)
        T_lower = T_available[T_available < T_HC].max()
        IM_HC_lower, MAF_HC_lower = getHazardCurveAtSite(IMname, soil, T_lower, 
                                                         Lat, Lon, threshold)
        IM_HC, MAF_HC = interpolateHazardCurve(IM_HC_lower, MAF_HC_lower, 
                                               IM_HC_upper, MAF_HC_upper,
                                               T_lower, T_upper, T_HC)
    return IM_HC, MAF_HC

	
def computeUHS(dataInput):
    '''
        Interpolates the hazard curve at every T, to get the UHS
    ''' 
    Lat = float(dataInput['Lat'])
    Lon = float(dataInput['Lon'])
    threshold = float(dataInput['threshold'])      # Threshold in °
    IMname = dataInput['IM']
    MAF_UHS = float(dataInput['MAF'])
    soil = dataInput['soil']
    
    try:
        T_UHS = T_UHS_ALL[IMname]
    except KeyError:
        raise KeyError("IM not supported: " + IMname)

    IM_UHS = np.zeros((len(T_UHS),1))
    for i,Ti in enumerate(T_UHS):
        GridLat,GridLon,IM,MAF = readHazardCurvesFromOQ(IMname, soil, Ti)
        dists = np.sqrt(np.square(GridLat-Lat) + np.square(GridLon-Lon))
        ndx = np.argwhere(dists < threshold)
        
        # Note that we will extrapolate values outside the HC's if needed
        f_int = [interpolate.interp1d(np.log(maf.squeeze()),np.log(IM), 
                           kind='linear', fill_value='extrapolate')
                                         for maf in MAF[ndx]]
        
        # IM_int is the map of IM's corresponding to MAF_UHS
        IM_int = [float(np.exp(f(np.log(MAF_UHS)))) for f in f_int]
        IM_UHS[i] = float(interpolateMap(Lat, Lon, GridLat[ndx], 
                          GridLon[ndx], IM_int))

    # Note: Maybe we should apply a smoothing method for the UHS
    # Answer: We solved this by plotting only some periods
    IM_UHS = IM_UHS.squeeze()
    
    # If IM is FIV3, then include FIV3 = 0 for T = 0
    if IMname == 'FIV3':
        T_UHS = (0,) + T_UHS
        IM_UHS = np.insert(IM_UHS, 0, 0)
        
    return T_UHS, IM_UHS
        

def getHazardCurveAtSite(IMname, soil, T, Lat, Lon, threshold):
    '''
        Interpolates the hazard curve at the specific site and T
    '''
    GridLat,GridLon,IM_HC,MAF = readHazardCurvesFromOQ(IMname, soil, T)
    dists = np.sqrt(np.square(GridLat-Lat) + np.square(GridLon-Lon))
    ndx = np.argwhere(dists < threshold)
    MAF_HC = np.zeros(IM_HC.shape)
    for i in range(0,len(IM_HC)):
        ind_notNull = notnull(MAF[ndx].T[i][0])     # Note that .T: transpose     
        if all(ind_notNull):
            ndx_notNull = ndx[ind_notNull]          # Indexes to use
            MAF_HC[i] = float(interpolateMap(Lat, Lon, GridLat[ndx_notNull], 
                          GridLon[ndx_notNull], MAF[ndx_notNull].T[i][0]))           
        else:
            MAF_HC[i] = float('111111')
            
    return IM_HC, MAF_HC
    

def interpolateHazardCurve(IM_l, MAF_l, IM_u, MAF_u, T_l, T_u, T):
    # Clean 111111 and 0 values
    IM_l = IM_l[MAF_l < 9999]
    MAF_l = MAF_l[MAF_l < 9999]
    IM_l = IM_l[MAF_l > 0]
    MAF_l = MAF_l[MAF_l > 0]
    IM_u = IM_u[MAF_u < 9999]
    MAF_u = MAF_u[MAF_u < 9999]
    IM_u = IM_u[MAF_u > 0]
    MAF_u = MAF_u[MAF_u > 0]
    
    maxMAF = min((max(MAF_l), max(MAF_u)))
    minMAF = max((min(MAF_l), min(MAF_u)))

    MAF_interp = np.exp(np.linspace(np.log(minMAF), np.log(maxMAF), 60))
    IM_l_func = interpolate.interp1d(np.log(MAF_l), np.log(IM_l))
    IM_l_interp = np.exp(IM_l_func(np.log(MAF_interp)))
    IM_u_func = interpolate.interp1d(np.log(MAF_u), np.log(IM_u))
    IM_u_interp = np.exp(IM_u_func(np.log(MAF_interp)))

    IM_t_interp = np.exp([np.log(im_l) + (np.log(im_u) - np.log(im_l)) / 
                          (np.log(T_u) - np.log(T_l)) * (np.log(T) - 
                           np.log(T_l)) for (im_l, im_u) in 
                           zip(IM_l_interp, IM_u_interp)])
    # Only report values 
    minIM = min(IM_t_interp)
    maxIM = max(IM_t_interp)
    IM_t = np.exp(np.linspace(np.log(minIM), np.log(maxIM), 30))
    MAF_t_func = interpolate.interp1d(np.log(IM_t_interp), 
                                      np.log(MAF_interp))     
    MAF_t = np.exp(MAF_t_func(np.log(IM_t)))
    
    return IM_t, MAF_t


def interpolateMap(LatQ, LonQ, GridLat, GridLon, Z):
    '''
        Interpolates Z, measured at grid points, at (LatQ,LonQ)
    '''
#    f_interp = interpolate.Rbf(GridLon,GridLat,Z,function='linear'
#                               ,smooth=0.0) # Only interpolation
#    return f_interp(LonQ,LatQ)   
    return interpolate.griddata((GridLon.squeeze(), GridLat.squeeze()), 
                                np.array(Z).squeeze(), (LonQ, LatQ),
                                method='linear')


def readHazardCurvesFromOQ(IMname, soil, T):
    '''
        Reads hazard curves at grid points from OQ output files
    '''
    filename = os.path.join(os.path.dirname(__file__), 'OQ-data', 'SFBA',
                            IMname, soil, 'hazard_curve-mean-' + IMname +
                            '-%.1f-.csv' % T)
    with open(filename, newline='') as f:
        data = csv.reader(f)
        headerLine = next(data)
        IMvaluesLine = next(data)

    Time = float(headerLine[1][20:])           # Investigation Time
    values = np.loadtxt(filename,skiprows=2,delimiter=',')
    
    GridLon = values[:,0]
    GridLat = values[:,1]
    PoE = values[:,3:]
    PoE2 = np.array([[x.squeeze() if x < 1 else float('nan')
                      for x in np.split(line,len(line))] for line in PoE])
    IM = np.array(list(float(text[4:]) for text in IMvaluesLine[3:]))
    MAF = -np.log(1-PoE2)/Time
        
    return GridLat,GridLon,IM,MAF
    

def main():
    inputfile = sys.argv[1]
    
    if inputfile.endswith('.json'):
        filename = inputfile
    else:
        filename = inputfile+'.json'
        
    with open(filename) as f:
        data = json.load(f)
    
    action = sys.argv[2]
    outputfile = sys.argv[3]
    
    assert action in ['-hc', '-uhs'], \
           'Action is not one of -hc or -uhs: ' + action
    
    if action == '-hc':
        IM_HC, MAF_HC = computeHazardCurve(data)
        dataToExport = {'IM': np.ndarray.tolist(IM_HC), 
                        'MAF': np.ndarray.tolist(MAF_HC)}
         
    elif action == '-uhs':
        
        # Note: Maybe we should apply a smoothing method for the UHS
        # Answer: We solved this by plotting only some periods
        T_UHS, IM_UHS = computeUHS(data)
        dataToExport = {'T': T_UHS, 
                        'IM': IM_UHS.squeeze().tolist()}

    if outputfile.endswith('.json'):
        filename = outputfile
    else:
        filename = outputfile+'.json'
        
    with open(filename, 'w') as outfile:
        json.dump(dataToExport, outfile, indent=4)

		
if __name__ == '__main__':
    import sys
    main()