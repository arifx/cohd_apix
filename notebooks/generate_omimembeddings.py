# -*- coding: utf-8 -*-

import numpy as np
import gensim
import pickle
import pandas as pd 
from cohd_helpers.cohd_requests import *
from cohd_helpers.cohd_temporal_analysis import *

def load_data(pklfile):
    f = open(pklfile, "rb")
    mydata = pickle.load(f)
    return mydata

def load_omim_omop_list(oolist_file):
    oo_listdata=pd.read_csv(oolist_file)
    return oo_listdata


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



#mce_matrix, mce_concept2id = load_mce("./node2vec_aug_128.txt", "node2vec")



#get omim-drug mappings
#wget.download("https://raw.githubusercontent.com/MaastrichtU-IDS/translator-openpredict/master/openpredict/data/resources/openpredict-omim-drug.csv")


def filter_omims_from_oolist():  
    omim_withemptyomop_list=load_omim_omop_list("./data/omim_withemptyomop.csv") # contains merged omim and empty omop=0 entries If there is no omop then its id is zero. 
    omimdf=omim_withemptyomop_list['omimid']

    for oid in omimdf:
      try:
        curie = "OMIM:"+str(oid)  # osteoarthritis
        _, df = xref_to_omop(curie, distance=2)
      except:
        print("OID error:"+str(oid))
      if df.empty != True:
        for omopid in df.omop_standard_concept_id:
          omim_withemptyomop_list.append([oid,omopid])
      else:
        print("Empty :"+str(oid))
        omim_withemptyomop_list.append([oid,0])

    omim_withemptyomop_table=pd.DataFrame(omim_withemptyomop_list, columns=['OMIMID','OMOPID'])

### Give OMIM-OMOP list and mce matrix, add omim ids and adds asa column, returns omim_mce_matrix, which contains
# only the interested OMIMs 
def add_omims_to_mce_matrix(omim_withemptyomop_list, mce_matrix, mce_concept2id):
    for omid in omim_withemptyomop_list["OMIMID"]:

        print(omim_withemptyomop_list[omid:])
        add_omims_to_mce_matrix=[]

    return add_omims_to_mce_matrix 

def get_omimids_to_concept2id(omim_withemptyomop_list,mce_concept2id):
    for omid,in omim_withemptyomop_list["OMIMID"] :
        print(omim_withemptyomop_list["omid"])
        omim_concept_embid = omim_withemptyomop_list["omid":]
    return omim_concept_embid 

def  __main__():
    mce_matrix, mce_concept2id = load_mce("./data/glove_e30_5year_128.npy", "glove",
                                     concept2id_path="./data/concept2id_condition_5yrs.pkl")
    omim_withemptyomop_table=pd.read_csv("./data/omim_withemptyomop.csv")
    print("All data loaded...")
    #omim_with_omopconceptids = add_omims_to_mce_matrix(omim_withemptyomop_table,mce_matrix,mce_concept2id)
    get_omimids_to_concept2id(omim_withemptyomop_table,mce_concept2id)
# find concepts from


__main__()