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
### get omoplist and average for each omim
def get_omimids_to_concept2id(oolist,mce_concept2id):
    omimembeddinglist_avereaged=[]
    for i in range(len(oolist)) :
        try:

            omid=oolist.loc[i,"OMIMID"]
            omopid=oolist.loc[i,"OMOPID"]
            embid=mce_concept2id[str(omopid)]
            #print("omopid,embeid:" + str(embid))
            
        except Exception as exc:

            pass    

    return [] 


def get_omop_embedding(oolist,mce_concept2id):
    omimembeddinglist=[]
    for i in range(len(oolist)) :
        try:
            omid=oolist.loc[i,"OMIMID"]
            omopid=oolist.loc[i,"OMOPID"]
            embid=mce_concept2id[str(omopid)]
            #print("omopid,embeid:" + str(embid))          
        except Exception as exc:
            pass    

    return [] 
def getEmbeddingIDfromOMOP(mce_concept2id,oid):
        return mce_concept2id[str(oid)]

    

def makeEmbeddingforOMOP(mce_matrix,omopid,mce_concept2id,embsize=128):
    EMBED_SIZE=embsize
   
    embed= np.zeros(EMBED_SIZE)
    try:
        eid=getEmbeddingIDfromOMOP(mce_concept2id,omopid)
        embed=mce_matrix[eid]    
    
    except Exception as idx:
        return -1
    return embed
def getOMOPListforOMIM(ol,omid):
    f=ol[ol["OMIMID"]==omid]
    omoplist=np.unique(f["OMOPID"])
    return omoplist

def calcAverageEmbedding(embeddingList):
    embaverage=embeddingList.average(axis=0)
    pass
    
def getAverageEmbeddingForOmimID(mce_matrix,mce_concept2id,omim_withemptyomop_df,omid):
    omoplist=getOMOPListforOMIM(omim_withemptyomop_df,omid)
    emblist=[]
    for oid in omoplist: 
        emb=makeEmbeddingforOMOP(mce_matrix,oid,mce_concept2id)
        if np.size(emb) > 1:
            emblist.append(emb)
    
    if np.size(emblist)!=0:
        embMean=np.mean(emblist,axis=0) 
    else:
        embMean=np.zeros(128) ## if no embedding avaiable , return zero embedding     
    return embMean


def getEmbeddingsDFforOmimSet(mce_matrix,mce_concept2id,omim_with_omopconceptids):
    entityURI="http:\/\/purl.bioontology.org\/ontology\/OMIM\/MTHU"
    uniqueOmims= np.unique(omim_with_omopconceptids["OMIMID"])
    omimEmbeddings=[]
    for omid in uniqueOmims:
        embMean=getAverageEmbeddingForOmimID(mce_matrix,mce_concept2id,omim_with_omopconceptids,omid)
        print("omim-id:embeddings:"+str(omid)+":"+str(embMean))
        omimEmbeddings.append([entityURI+str(omid),embMean])
    #convert to data frame
    omimEmbeddingsDF=pd.DataFrame(omimEmbeddings,columns=['entity','embedding'])
    return omimEmbeddingsDF


###generate glove embeddings in json format
# get omim glove embeddings in data frame format
# convert to Translator OpenPredict JSON Format
# write to json file
###
def saveEmbeddings_to_JSON(mce_matrix,mce_concept2id,omim_with_omopconceptids, jsonfilenamepath):
    response=0
    try:
        omimEmbeddingsDF= getEmbeddingsDFforOmimSet(mce_matrix,mce_concept2id,omim_with_omopconceptids)
        omimEmbeddingsDF.to_json(jsonfilenamepath,orient='records')   
        response=1
    except Exception as identifier:
        response=0
   
    return response


###
# Get embeddings for TOP omim ids,
# if embedding does not exist it is filled with zeros
# mce_matrix contains glove embeddings for all concepts with ids.
# mce_concept2id converts conceptid(OMOP id) to embedding id
# omim_with_emptyomop_table: onetomany OMIM->OMOP mappings. Some OMIMs are not found in OMOP. They are also kept in the table for reverse conversion,    
###


def __main__():
    mce_matrix, mce_concept2id = load_mce("./data/glove_e30_5year_128.npy", "glove",
                                     concept2id_path="./data/concept2id_condition_5yrs.pkl")
    omim_withemptyomop_df=pd.read_csv("./data/omim_withemptyomop.csv")
    print("All data loaded...")
    #omim_with_omopconceptids = add_omims_to_mce_matrix(omim_withemptyomop_table,mce_matrix,mce_concept2id)
    # give coceptid get embedding
    
    omid=600263
    omimEmbed=getAverageEmbeddingForOmimID(mce_matrix,mce_concept2id,omim_withemptyomop_df,omid)
    jsonfilenamepath="./omim_gloveembeddings.json"
    #omimEmbeddings=getEmbeddingsDFforOmimSet(mce_matrix,mce_concept2id,omim_withemptyomop_df)

    saveResult=saveEmbeddings_to_JSON(mce_matrix,mce_concept2id,omim_withemptyomop_df, jsonfilenamepath)
    print("Embedding File generated?:"+str(saveResult))   
 




__main__()