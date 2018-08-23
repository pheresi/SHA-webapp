#!/usr/bin/env python3

import sys
import cgi
import json
import numpy as np
import interpolator_functions as in_fn
#from pathlib import Path
#from nose.tools import set_trace
 

# Information comming from Ajax request
fs = cgi.FieldStorage();

sys.stdout.write("Content-Type: application/json")

sys.stdout.write("\n")
sys.stdout.write("\n")

# get the information coming from data 
result = {}

d = {}
for k in fs.keys():
    d[k] = fs.getvalue(k)

result['data'] = d

if d['action'] == '-hc':

    IM_HC, MAF_HC = in_fn.computeHazardCurve(result['data'])
    dataToExport = {'IM': np.ndarray.tolist(IM_HC), 
                    'MAF': np.ndarray.tolist(MAF_HC)}

    # Careful here, returning only IM and MAF, by dumping
    # "result" the keys can be return as well.                 
    resultout = {}
    resultout['IM']  = dataToExport['IM']
    resultout['MAF'] = dataToExport['MAF']

    sys.stdout.write(json.dumps(resultout,indent=2,allow_nan=True))
    sys.stdout.close()

elif d['action'] == '-uhs':

    T_UHS, IM_UHS = in_fn.computeUHS(result['data'])
    dataToExport = {'T': T_UHS, 
                    'IM': IM_UHS.squeeze().tolist()}

    # Careful here, returning only IM and MAF, by dumping
    # "result" the keys can be return as well.                 
    resultout = {}
    resultout['T']  = dataToExport['T']
    resultout['IM'] = dataToExport['IM']

    # sys.stdout.write("\n")

    sys.stdout.write(json.dumps(resultout,indent=2,allow_nan=True))
    sys.stdout.close()