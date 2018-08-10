import numpy as np
import csv
from pandas import notnull
from scipy import interpolate
# from nose.tools import set_trace

class interpolator:
    
    def __init__(self,InputFilename):
        '''
            Opens the file 'filename' and reads the inputs
        '''
        if InputFilename.endswith('.csv'):
            filename = InputFilename
        else:
            filename = InputFilename+'.csv'
            
        with open(filename, newline='') as csvfile:
            data = list(csv.reader(csvfile))
            
        self.Lat = float(data[0][0])
        self.Lon = float(data[0][1])
        self.threshold = float(data[0][2])      # Threshold in °
        self.IMname = data[0][3]
        self.T_HC = float(data[0][4])
        self.IM_HC = []
        self.MAF_HC = []
        self.MAF_UHS = float(data[0][5])
        self.T_UHS = np.array(list(map(float, data[1])))
        self.IM_UHS = []

    def computeHazardCurve(self):
        '''
            Interpolates the hazard curve
        '''
        Lats,Lons,IM,MAF = self.readHazardCurvesFromOQ(self.T_HC)
        dists = np.sqrt(np.square(Lats-self.Lat) + np.square(Lons-self.Lon))
        ndx = np.argwhere(dists < self.threshold)

        self.IM_HC = IM
        self.MAF_HC = np.zeros(IM.shape)
        for i in range(0,len(IM)):
            ind_notNull = notnull(MAF[ndx].T[i][0])        
            if all(ind_notNull):
                ndx_notNull = ndx[ind_notNull]  # Indexes to use
                self.MAF_HC[i] = float(self.interpolateMap(self.Lat, self.Lon, 
                           Lats[ndx_notNull], Lons[ndx_notNull], 
                           MAF[ndx_notNull].T[i][0]))
            else:
                self.MAF_HC[i] = float('nan')
                
        return ndx

    def computeUHS(self):
        '''
            Interpolates the hazard curve at every T, to get the UHS
        '''
        self.IM_UHS = np.zeros(self.T_UHS.shape)
        IM_int_all = [];
        for i,Ti in enumerate(self.T_UHS):
            Lats,Lons,IM,MAF = self.readHazardCurvesFromOQ(Ti)
            dists = np.sqrt(np.square(Lats-self.Lat) + 
                            np.square(Lons-self.Lon))
            ndx = np.argwhere(dists < self.threshold)
            
            # Note that we will extrapolate values outside the HC's if needed
            f_int = [interpolate.interp1d(np.log(maf.squeeze()),np.log(IM), 
                               kind='linear', fill_value='extrapolate')
                                             for maf in MAF[ndx]]
            
            # IM_int is the map of IM's corresponding to self.MAF_UHS
            IM_int = [float(np.exp(f(np.log(self.MAF_UHS)))) for f in f_int]


            self.IM_UHS[i] = float(self.interpolateMap(self.Lat, self.Lon, 
                                   Lats[ndx], Lons[ndx], IM_int))
            IM_int_all.append(IM_int)
        
        return IM_int_all
    
    
    def interpolateMap(self, LatQ, LonQ, Lats, Lons, Z):
        f_interp = interpolate.Rbf(Lons,Lats,Z,function='linear'
                                   ,smooth=0.0) # Only interpolation
#        f_interp = interpolate.interp2d(Lons,Lats,Z)
        return f_interp(LonQ,LatQ)

    def readHazardCurvesFromOQ(self,T):
        filename = "hazard_curve-rlz-000-"+self.IMname+"(%.1f).csv" % T
        with open(filename, newline='') as f:
            data = csv.reader(f)
            headerLine = next(data)
            IMvaluesLine = next(data)
            
        Time = float(headerLine[4][20:])           # Investigation Time
        values =    np.loadtxt(filename,skiprows=2,delimiter=',')
        
        Lons = values[:,0]
        Lats = values[:,1]
        PoE = values[:,3:]
        PoE2 = np.array([[x if x < 1 else float('nan')
                          for x in np.split(line,len(line))] for line in PoE])
        
        IM = np.array(list(float(text[4:]) for text in IMvaluesLine[3:]))

        MAF = -np.log(1-PoE2)/Time
            
        return Lats,Lons,IM,MAF
    

    def exportHazardCurve(self,filename_HC):
        if filename_HC.endswith('.csv'):
            filename = filename_HC
        else:
            filename = filename_HC+'.csv'
            
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Hazard Curve for '+self.IMname+
                                           '({0})'.format(self.T_HC)])
            writer.writerow(self.IM_HC)
            writer.writerow(self.MAF_HC)
        print('Hazard Curve exported')

    def exportUHS(self,filename_UHS):
        if filename_UHS.endswith('.csv'):
            filename = filename_UHS
        else:
            filename = filename_UHS+'.csv'
            
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Uniform Hazard Spectrum for '+self.IMname+
                                        ' - MAF = {0}'.format(self.MAF_UHS)])
            writer.writerow(self.T_UHS)
            writer.writerow(self.IM_UHS)
        print('Uniform Hazard Spectrum exported')


def main():
    inputfile = sys.argv[1]
    action = sys.argv[2]
    filename_output = sys.argv[3]
    
    assert action in ['--hc', '--uhs', '--hc&uhs'], \
           'Action is not one of --hc, --uhs, or --hc&uhs: ' + action
    
    interp = interpolator(inputfile)
    if action == '--hc':
        interp.computeHazardCurve()
        interp.exportHazardCurve(filename_output)
    elif action == '--uhs':
        interp.computeUHS()
        interp.exportUHS(filename_output)
    elif action == '--hc&uhs':
        interp.computeHazardCurve()
        interp.exportHazardCurve(filename_output)
        filename_output2 = sys.argv[4]
        interp.computeUHS()
        interp.exportUHS(filename_output2)
    
    
if __name__ == '__main__':
    import sys
    main()