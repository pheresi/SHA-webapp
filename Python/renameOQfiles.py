import os
from pathlib import Path

IMname = 'FIV3'
Zone = 'SFBA'


#%% Rename everything

path = Path('OQ-data/' + IMname + '/' + Zone)
files = os.listdir(path)

for file in files:
    fileNew = file
    fileNew = fileNew.replace('(','-')
    fileNew = fileNew.replace(')','-')
    ind_ = fileNew.rfind('_')
    if fileNew[:ind_] != 'hazard':
        fileNew = fileNew[:ind_]+'.csv'
    
    print(fileNew)
    os.rename(path / file, path / fileNew)