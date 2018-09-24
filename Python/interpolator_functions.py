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
    
    GridLat,GridLon,IM_HC,MAF = readHazardCurvesFromOQ(IMname, soil, T_HC)
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
        print("IM not supported for UHS")
        raise

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