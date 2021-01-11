import functions
import dic
import LoadYml
import yaml
import json
import re
import pandas as pd
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer)
from sklearn.metrics.pairwise import cosine_similarity

settingsFile = "settings.yml"
settings = yaml.safe_load(open(settingsFile))
memexPath = settings["path_to_memex"]
language = settings["language_keys"]


#min_Df_S = settings["min_df"]
#max_Df_S = settings["max_df"]

stopWFile = "Stopwords_German.txt"
stopwordsList = open(stopWFile, "r", encoding="utf8").read().split("\n")


def generatetfidfvalues():

    ocrFiles = functions.dicOfRelevantFiles(memexPath, ".json")
    citeKeys = list(ocrFiles.keys()) #list with the citeKeys 
    #print(citeKeys)

    docList   = [] #for the content
    docIdList = [] #for the citationkeys

    for citeKey in citeKeys: #loops through the citeKeys
        docData = json.load(open(ocrFiles[citeKey], "r", encoding="utf8"))
    
        docId = citeKey
        doc   = " ".join(docData.values())

        #cleaning the text:
        doc = re.sub(r'(\w)-\n(\w)', r'\1\2', doc)
        doc = re.sub('\W+', ' ', doc)
        doc = re.sub('\d+', ' ', doc)
        doc = re.sub(' +', ' ', doc)

        docList.append(doc)
        docIdList.append(docId)

    #print(docList) # '...', '...' includes the text
    #print(docIdList) # '...' includes the citation Keys

    #creates a matrix with tf-idf-values
    vectorizer = CountVectorizer(ngram_range=(1,1), min_df=5, max_df=0.5)#, stop_words=stopWFile) #only unigrams will be considered, setting of minimum and maximum values
    countVectorized = vectorizer.fit_transform(docList)
    tfidfTransformer = TfidfTransformer(smooth_idf=True, use_idf=True)
    vectorized = tfidfTransformer.fit_transform(countVectorized) # https://en.wikipedia.org/wiki/Sparse_matrix #stores the tf-idf values in a sparse matrix
    cosineMatrix = cosine_similarity(vectorized) #stores a symmetric matrix of cosine distances

    #converts the tfidf-matrix into a dictionary
    tfidfTable = pd.DataFrame(vectorized.toarray(), index=docIdList, columns=vectorizer.get_feature_names())
    print("tfidfTable Shape: ", tfidfTable.shape) # optional, in my case (31, 3268)
    tfidfTable = tfidfTable.transpose()
    tfidfTableDic = tfidfTable.to_dict()

    #converts the cosine-distance-matrix into a dictionary
    cosineTable = pd.DataFrame(cosineMatrix)
    print("cosineTable Shape: ", cosineTable.shape) # optional, in my case (31, 31)
    cosineTable.columns = docIdList
    cosineTable.index = docIdList
    cosineTableDic = cosineTable.to_dict()

    filteredDic = {}
    filteredDic = functions.filterDic(tfidfTableDic, 0.08)
    with open("tfidfTableDic_filtered3.txt", 'w', encoding='utf8') as f9:
        json.dump(filteredDic, f9, sort_keys=True, indent=4, ensure_ascii=False)    
    filteredDic = {}
    filteredDic = functions.filterDic(cosineTableDic, 0.18)    
    with open("cosineTableDic_filtered3.txt", 'w', encoding='utf8') as f9:
        json.dump(filteredDic, f9, sort_keys=True, indent=4, ensure_ascii=False)
        
        
generatetfidfvalues()

    #keywordsDic = {}

    #for docIdList in tfidfTableDic:     # term frequencies 
      #  if #value  >= 0.05:             # if values are higher than 0.05 add to dictionary
     #       keywordsDic[docIdList] = #value ? ## docIdList as key 
    #print(keywordsDic)

   # with open(jsonFile, 'w', encoding='utf8') as f9:
    # json.dump(textResults, f9, sort_keys=True, indent=4, ensure_ascii=False)
    
    #distancesDic = {}

    #for docIdList in cosineTableDic:   # distance 
      #  if  cosineMatrix  < 1:         # if the value is under 1
     #       if cosineMatrix > 1/4:     # and over 0.25
    #            distancesDic[docIdList] = cosineMatrix    # add the value? docIdList as key? 
        
    #print(distancesDic)
        

    #put into json file, but not with extentions json 
    #with open(jsonFile, 'w', encoding='utf8') as f9:
     #       json.dump(textResults, f9, sort_keys=True, indent=4, ensure_ascii=False)
    

#loop through the dictionary
#create a new dictionary with only relevant tfidf values and distance values between your texts
#save your dictionary to a json-file


