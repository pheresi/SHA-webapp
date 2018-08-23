import unittest
#import unittest.mock as um
import os
from pathlib import Path

import numpy as np
#import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import Axes3D
#from scipy import interpolate
#from nose.tools import set_trace

import interpolator_functions as inter

GridLat_FAKE = np.array((0, 0.2, 0, 0.2, -0.2, -0.2))
GridLon_FAKE = np.array((-0.1, -0.1, 0.1, 0.1, -0.1, 0.1))
IM_FAKE = np.array((1,10,100,1000,10000))
MAF_FAKE = np.array([[float('nan'),8E-2,8E-3,8E-4,0],
                     [float('nan'),6E-2,6E-3,6E-4,0],
                     [float('nan'),6E-2,6E-3,6E-4,0],
                     [float('nan'),4E-2,4E-3,4E-4,0],
                     [float('nan'),8E-2,8E-3,8E-4,0],
                     [float('nan'),6E-2,6E-3,6E-4,0]])

FakeHCtext = "# source_model_tree_path=('ltbrTrueMean',), gsim_tree_path=" +\
"('b1',), investigation_time=1.0, imt=\"TestIM(1.0)\"\n" +\
"lon,lat,depth,poe-1,poe-10,poe-100,poe-1000,poe-10000\n" +\
"-0.1,0,0,1,7.69E-02,7.97E-03,8.00E-04,0.00E+00\n" +\
"-0.1,0.2,0,1,5.82E-02,5.98E-03,6.00E-04,0.00E+00\n" +\
"0.1,0,0,1,5.82E-02,5.98E-03,6.00E-04,0.00E+00\n" +\
"0.1,0.2,0,1,3.92E-02,3.99E-03,4.00E-04,0.00E+00\n" +\
"-0.1,-0.2,0,1,7.69E-02,7.97E-03,8.00E-04,0.00E+00\n" +\
"0.1,-0.2,0,1,5.82E-02,5.98E-03,6.00E-04,0.00E+00"

FakeHCtext2 = "# source_model_tree_path=('ltbrTrueMean',), gsim_tree_path=" +\
"('b1',), investigation_time=1.0, imt=\"TestIM(2.0)\"\n" +\
"lon,lat,depth,poe-2,poe-20,poe-200,poe-2000,poe-20000\n" +\
"-0.1,0,0,1,7.69E-02,7.97E-03,8.00E-04,0.00E+00\n" +\
"-0.1,0.2,0,1,5.82E-02,5.98E-03,6.00E-04,0.00E+00\n" +\
"0.1,0,0,1,5.82E-02,5.98E-03,6.00E-04,0.00E+00\n" +\
"0.1,0.2,0,1,3.92E-02,3.99E-03,4.00E-04,0.00E+00\n" +\
"-0.1,-0.2,0,1,7.69E-02,7.97E-03,8.00E-04,0.00E+00\n" +\
"0.1,-0.2,0,1,5.82E-02,5.98E-03,6.00E-04,0.00E+00"

FakeHCtext3 = "# source_model_tree_path=('ltbrTrueMean',), gsim_tree_path=" +\
"('b1',), investigation_time=1.0, imt=\"TestIM(3.0)\"\n" +\
"lon,lat,depth,poe-0.5,poe-5,poe-50,poe-500,poe-5000\n" +\
"-0.1,0,0,1,7.69E-02,7.97E-03,8.00E-04,0.00E+00\n" +\
"-0.1,0.2,0,1,5.82E-02,5.98E-03,6.00E-04,0.00E+00\n" +\
"0.1,0,0,1,5.82E-02,5.98E-03,6.00E-04,0.00E+00\n" +\
"0.1,0.2,0,1,3.92E-02,3.99E-03,4.00E-04,0.00E+00\n" +\
"-0.1,-0.2,0,1,7.69E-02,7.97E-03,8.00E-04,0.00E+00\n" +\
"0.1,-0.2,0,1,5.82E-02,5.98E-03,6.00E-04,0.00E+00"

class interpolatorTestCase(unittest.TestCase):
    
    def test_computeHC(self):
        fakeHCname = 'hazard_curve-rlz-000-TestIM-1.0-.csv'
        fake_HCfromOQ = open(fakeHCname, "w")
        fake_HCfromOQ.write(FakeHCtext)
        fake_HCfromOQ.close()
        data_folder = Path("OQ-data/TestIM/SFBA/")
        os.rename(fakeHCname, data_folder / fakeHCname)
        
        LonQs = (0,-0.1,0,0.1,0,0)
        LatQs = (0,0.1,0.1,0.1,0.2,0.05)
        MAF_expected = (np.array((111111,7E-2,7E-3,7E-4,0)),
                        np.array((111111,7E-2,7E-3,7E-4,0)),
                        np.array((111111,6E-2,6E-3,6E-4,0)),
                        np.array((111111,5E-2,5E-3,5E-4,0)),
                        np.array((111111,5E-2,5E-3,5E-4,0)),
                        np.array((111111,6.5E-2,6.5E-3,6.5E-4,0)))
        MAF_HC_all = []
        dataInput = {}
        for LonQ,LatQ,MAFexp in zip(LonQs,LatQs,MAF_expected):     
            dataInput['Lat'] = str(LatQ)
            dataInput['Lon'] = str(LonQ)
            dataInput['threshold'] = '0.5'
            dataInput['IM'] = 'TestIM'
            dataInput['T'] = '1'
                        
#            with um.patch('interpolator.readHazardCurvesFromOQ',return_value= 
#                             (GridLat_FAKE, GridLon_FAKE, IM_FAKE, MAF_FAKE)):           
            IM_HC, MAF_HC = inter.computeHazardCurve(dataInput)
            MAF_HC_all.append(MAF_HC)
            
        os.remove(data_folder / fakeHCname)
        
        for result,expected in zip(MAF_HC_all,MAF_expected):
            np.testing.assert_allclose(result, expected, rtol=5e-03)                    

#        fig = plt.figure()
#        ax = fig.add_subplot(111, projection='3d')
#        ax.scatter(GridLon_FAKE,GridLat_FAKE,MAF_FAKE.T[1],c='r',marker='o')
#        ax.scatter(LonQ,LatQ,MAF_HC[1],'or')
#        LonsNew, LatsNew = np.mgrid[-0.1:0.1:50j, -0.2:0.2:100j]
#        fnew = inter.interpolateMap(LatsNew.ravel(), LonsNew.ravel(), 
#                                    GridLat_FAKE, GridLon_FAKE, MAF_FAKE.T[1])
#        ax.plot_surface(LonsNew,LatsNew,fnew.reshape(LonsNew.shape),alpha=0.3)
#        ax.set_xlabel('Lon [°]')
#        ax.set_ylabel('Lat [°]')
#        ax.set_zlabel('MAF[end]')
                             
        
    def test_computeUHS(self):
        fakeHCname1 = 'hazard_curve-rlz-000-TestIM-1.0-.csv'
        fake_HCfromOQ = open(fakeHCname1, "w")
        fake_HCfromOQ.write(FakeHCtext)
        fake_HCfromOQ.close()
        data_folder = Path("OQ-data/TestIM/SFBA/")
        os.rename(fakeHCname1, data_folder / fakeHCname1)        
        fakeHCname2 = 'hazard_curve-rlz-000-TestIM-2.0-.csv'
        fake_HCfromOQ = open(fakeHCname2, "w")
        fake_HCfromOQ.write(FakeHCtext2)
        fake_HCfromOQ.close()
        data_folder = Path("OQ-data/TestIM/SFBA/")
        os.rename(fakeHCname2, data_folder / fakeHCname2)
        fakeHCname3 = 'hazard_curve-rlz-000-TestIM-3.0-.csv'
        fake_HCfromOQ = open(fakeHCname3, "w")
        fake_HCfromOQ.write(FakeHCtext3)
        fake_HCfromOQ.close()
        data_folder = Path("OQ-data/TestIM/SFBA/")
        os.rename(fakeHCname3, data_folder / fakeHCname3) 

        LonQs = (0,-0.1,0,0.1,0,0)
        LatQs = (0,0.1,0.1,0.1,0.2,0.05)
        MAF_UHS = (7e-3,7e-3,6e-3,5e-3,5e-3,6.5e-3)
        IM_UHS_expected = np.array((100,200.2,49.8))
        IM_UHS_all = []
        dataInput = {}
        for LonQ,LatQ,maf in zip(LonQs,LatQs,MAF_UHS):  
            dataInput['Lat'] = str(LatQ)
            dataInput['Lon'] = str(LonQ)
            dataInput['threshold'] = '0.5'
            dataInput['IM'] = 'TestIM'
            dataInput['MAF'] = str(maf)   
            T_UHS, IM_UHS = inter.computeUHS(dataInput)
            IM_UHS_all.append(IM_UHS)
            
        os.remove(data_folder / fakeHCname1)
        os.remove(data_folder / fakeHCname2)
        os.remove(data_folder / fakeHCname3)

        for im_uhs_result in IM_UHS_all:
            np.testing.assert_allclose(im_uhs_result, IM_UHS_expected,
                                       rtol=5e-03)
