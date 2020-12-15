# -*- coding: utf-8 -*-

import numpy as np
import gensim
import pickle
import pandas as pd 

def load_data(pklfile):
    f = open(pklfile, "rb")
    mydata = pickle.load(f)
    return mydata

def build_dict(concept_list):
    mydict = dict()

    for idx, concept in enumerate(concept_list):
        mydict[concept] = idx
    
    return mydict

def load_mce(mce_data_path, data_format, concept2id_path=None):

    if data_format in ["glove", "skipgram", "svd"]:
        mce_matrix = np.load(mce_data_path)
        if concept2id_path != None:
            concept2id = load_data(concept2id_path)
        else:
            print("concept2id must be provided if data format is npy")

    elif data_format in ["line", "node2vec"]:
        mce = gensim.models.KeyedVectors.load_word2vec_format(mce_data_path)
        concept2id = build_dict(list(mce.vocab))

        mce_matrix = np.zeros((len(concept2id), mce.vector_size))

        for concept in list(concept2id.keys()):
            mce_matrix[concept2id[concept]] = mce[concept]

    return mce_matrix, concept2id

mce_matrix, mce_concept2id = load_mce("./glove_e30_5year_128.npy", "glove",
                                     concept2id_path="./concept2id_condition_5yrs.pkl")

#mce_matrix, mce_concept2id = load_mce("./node2vec_aug_128.txt", "node2vec")



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


