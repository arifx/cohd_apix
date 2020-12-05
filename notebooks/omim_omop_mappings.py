import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import copy
from cohd_helpers.cohd_requests import *
from cohd_helpers.cohd_temporal_analysis import *
import time as timer
import wget #pip install wget



#get omim-drug mappings
#wget.download("https://raw.githubusercontent.com/MaastrichtU-IDS/translator-openpredict/master/openpredict/data/resources/openpredict-omim-drug.csv")


omimomoplist=[]
empty_omim_list=[]
omim_withemptyomop_list=[] # contains merged omim and empty omop=0 entries If there is no omop then its id is zero. 
data = pd.read_csv("openpredict-omim-drug.csv") 
#print("omimcount:"+str(data.count))
omimdf=data['omimid']

print(str(omimdf.head()))

for oid in omimdf:
  #timer.sleep(1)
  #print("OMIMID->"+str(oid))
  try:
    curie = "OMIM:"+str(oid)  # osteoarthritis
    _, df = xref_to_omop(curie, distance=2)
  except:
    print("OID error:"+str(oid))
  if df.empty != True:
    for omopid in df.omop_standard_concept_id:
      omimomoplist.append([oid,omopid])
      omim_withemptyomop_list.append([oid,omopid])
  else:
    print("Empty OMIM:"+str(oid))
    empty_omim_list.append(oid)
    omim_withemptyomop_list.append([oid,0])

omim_omop_table=pd.DataFrame(omimomoplist, columns=['OMIMID','OMOPID'])
omim_withemptyomop_table=pd.DataFrame(omim_withemptyomop_list, columns=['OMIMID','OMOPID'])
empty_omim_table=pd.DataFrame(empty_omim_list, columns=['OMIMID'])
#print(omim_omop_table.count)
#print(empty_omim_list.count)

#print("table:"+ str(omim_omop_table))
omim_withemptyomop_store = pd.HDFStore('omim_withempty_omop_store.h5')
omim_omop_store = pd.HDFStore('omim_omop__store.h5')
empty_omims_store= pd.HDFStore('empty_omims_store.h5')

omim_omop_store['omim_omop_store'] = omim_omop_table  # save it
empty_omims_store['empty_omims_store'] = empty_omim_table  # save it
omim_withemptyomop_store['omim_omop_store'] = omim_withemptyomop_table  # save it

omim_omop_table.to_csv("omim_omop_table.csv")
empty_omim_table.to_csv("empty_omim_table.csv")
omim_withemptyomop_table.to_csv("omim_withemptyomop.csv")
