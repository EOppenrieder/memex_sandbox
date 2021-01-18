# NEW LIBRARIES
import pandas as pd #import the panda library
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer) #import a feature from the sklearn-library for transforming your data
from sklearn.metrics.pairwise import cosine_similarity #import the cosine_similarity feature from the sklearn-library

import os, json, re, sys #import various other libraries

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions #import the script with our previous functions

###########################################################
# VARIABLES ###############################################
###########################################################

settings = functions.loadYmlSettings("settings.yml") #load  our settings file

###########################################################
# MAIN FUNCTIONS ##########################################
###########################################################

def filterTfidfDictionary(dictionary, threshold, lessOrMore): #define a function for the filtering of our tf-idf-dictionary
    dictionaryFilt = {} #create an empty dictionary
    for item1, citeKeyDist in dictionary.items(): #loop through the outer dictionary which contains the title of each publication
        dictionaryFilt[item1] = {} #create a subdictionary for each publication
        for item2, value in citeKeyDist.items(): #loop through that subdictionary
            if lessOrMore == "less": #check for the lower threshold
                if value <= threshold: #proceed if the value is below the threshold
                    if item1 != item2: #proceed if it is not the same publication 
                        dictionaryFilt[item1][item2] = value #add the value 
            elif lessOrMore == "more": #check for the upper threshold
                if value >= threshold: #proceed if the value is above the threshold
                    if item1 != item2: #proceed if it is not the same publication                        
                        dictionaryFilt[item1][item2] = value #add the value
            else:
                sys.exit("`lessOrMore` parameter must be `less` or `more`") #exit the code so you can check for errors in your code

        if dictionaryFilt[item1] == {}: #check if the subdictionary is empty
            dictionaryFilt.pop(item1) #remove this item in the dictionary and return it
    return(dictionaryFilt) #return the dictionary


def tfidfPublications(pathToMemex): #create the tfidf-dictionary
    # PART 1: loading OCR files into a corpus
    ocrFiles = functions.dicOfRelevantFiles(pathToMemex, ".json") #generate a dictionary with citekeys as keys and paths to json-Files as values
    citeKeys = list(ocrFiles.keys())#[:500] #create a list with the citeKeys

    print("\taggregating texts into documents...") #print to inform about the processing
    docList   = [] #create an empty list for the content of the publications
    docIdList = [] #create an empty list for the citeKeys

    for citeKey in citeKeys: #loop through the citeKeys
        docData = json.load(open(ocrFiles[citeKey])) #load the OCRed results of the publications
        # IF YOU ARE ON WINDOWS, THE LINE SHOULD BE:
        # docData = json.load(open(ocrFiles[citeKey], "r", encoding="utf8"))
        
        docId = citeKey #take the citeKey of each publication
        doc   = " ".join(docData.values()) #take the OCRed content of each publication

        # clean doc
        doc = re.sub(r'(\w)-\n(\w)', r'\1\2', doc)
        doc = re.sub('\W+', ' ', doc)
        doc = re.sub('_+', ' ', doc)
        doc = re.sub('\d+', ' ', doc)
        doc = re.sub(' +', ' ', doc) #clean your content with the help of regular expressions, especially remove unneccessary blanks and signs)

        # update lists
        docList.append(doc) #add the content of each publication to the first list
        docIdList.append(docId) #add the citeKey of each publication to the second key

    print("\t%d documents generated..." % len(docList)) #print the number of publications

    # PART 2: calculate tfidf for all loaded publications and distances
    print("\tgenerating tfidf matrix & distances...") #print to inform about the processing
    vectorizer = CountVectorizer(ngram_range=(1,1), min_df=5, max_df=0.5) #create a vectorizer (use only unigrams, use only words that appear in at least five documents, use only words that appear in less than half of all documents)
    countVectorized = vectorizer.fit_transform(docList) #create the vectors
    tfidfTransformer = TfidfTransformer(smooth_idf=True, use_idf=True) #adjust the transformer
    vectorized = tfidfTransformer.fit_transform(countVectorized) # generate a sparse matrix with tfidf-values
    cosineMatrix = cosine_similarity(vectorized) #generate a matrix with cosine distance values

    # PART 3: saving TFIDF
    print("\tsaving tfidf data...") #print to inform about the processing
    tfidfTable = pd.DataFrame(vectorized.toarray(), index=docIdList, columns=vectorizer.get_feature_names()) #transform the matrix into a dataframe
    tfidfTable = tfidfTable.transpose() #transpose rows and columns to document and information
    print("\ttfidfTable Shape: ", tfidfTable.shape) #print the shape of the dataframe
    tfidfTableDic = tfidfTable.to_dict() #create a dictionary with the tfidf-values

    tfidfTableDicFilt = filterTfidfDictionary(tfidfTableDic, 0.05, "more") #use the previously defined function to filter the tf-idf dictionary, include only words with a tf-idf value higher than 0.05 
    pathToSave = os.path.join(pathToMemex, "results_tfidf.dataJson") #create the filepath and the filename
    with open(pathToSave, 'w', encoding='utf8') as f9:
        json.dump(tfidfTableDicFilt, f9, sort_keys=True, indent=4, ensure_ascii=False) #create the json-File which saves your filtered tfidf dictionary

    # PART 3: saving cosine distances
    print("\tsaving cosine distances data...") #print to inform about the processing
    cosineTable = pd.DataFrame(cosineMatrix) #transform the matrix into a dataframe
    print("\tcosineTable Shape: ", cosineTable.shape) #print the shape of the dataframe
    cosineTable.columns = docIdList #take the list with the citeKeys as columns
    cosineTable.index = docIdList #take the list with the citeKeys as index
    cosineTableDic = cosineTable.to_dict() #create a dictionary with the cosine similarity values

    tfidfTableDicFilt = filterTfidfDictionary(cosineTableDic, 0.25, "more") #use the previously defined function to filter the cosine similarities dictionary, include only publications with a cosine similarity value higher than 0.25
    pathToSave = os.path.join(pathToMemex, "results_cosineDist.dataJson") #create the filepath and the filename
    with open(pathToSave, 'w', encoding='utf8') as f9:
        json.dump(tfidfTableDicFilt, f9, sort_keys=True, indent=4, ensure_ascii=False) #create the json-File which saves your filtered cosine similarities dictionary

tfidfPublications(settings["path_to_memex"]) #execute the function