# -*- coding: utf-8 -*-

import numpy as np
import gensim
import pickle

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

mce_matrix, mce_concept2id = load_mce("~/glove_e30_5year_128.npy", "glove",
                                     concept2id_path="~/concept2id_condition_5yrs.pkl")

mce_matrix, mce_concept2id = load_mce("~/node2vec_aug_128.txt", "node2vec")
