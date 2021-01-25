# NEW LIBRARIES
import pandas as pd #import the pandas library
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer) #import a feature from the sklearn-library for transforming your data
from sklearn.metrics.pairwise import cosine_similarity #import the cosine_similarity feature from the sklearn-library

import os, json, re, random #import various other libraries

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions #import the script with our previous functions

###########################################################
# VARIABLES ###############################################
###########################################################

settings = functions.loadYmlSettings("settings.yml") #load  our settings file

###########################################################
# MAIN FUNCTIONS ##########################################
###########################################################

from wordcloud import WordCloud #import the WordCloud feature from the wordcloud library
import matplotlib.pyplot as plt #import the matplotlib library

def generateWordCloud(citeKey, pathToFile): #define a function that creates wordclouds
    # aggregate dictionary
    data = json.load(open(pathToFile)) #load the OCRed publication
    dataNew = {} #create an empty dictionary
    for page,pageDic in data.items(): #loop through the pages of the publication
        for term, tfIdf in pageDic.items(): #loop through terms and tfidf values
            if term in dataNew: #check if the term is in the new dictionary
                dataNew[term] += tfIdf #add (additionally) the tfidf value
            else:
                dataNew[term]  = tfIdf #add the tfidf value

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


def generateTfIdfWordClouds(pathToMemex): #define a function that creates wordclouds according to the tfidf values
    # PART 1: loading OCR files into a corpus
    ocrFiles = functions.dicOfRelevantFiles(pathToMemex, ".json") #generate a dictionary with citekeys as keys and paths to json-Files as values
    citeKeys = list(ocrFiles.keys())#[:500] #create a list with the citeKeys

    print("\taggregating texts into documents...") #print to inform about the processing
    docList   = [] #create an empty list for the content of the publications
    docIdList = [] #create an empty list for the citeKeys

    for citeKey in citeKeys: #loop through the citeKeys
        docData = json.load(open(ocrFiles[citeKey])) #load the OCRed results of the publications
        
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

    print("\tconverting and filtering tfidf data...") #print to inform about the processing
    tfidfTable = pd.DataFrame(vectorized.toarray(), index=docIdList, columns=vectorizer.get_feature_names()) #transform the matrix into a dataframe
    tfidfTable = tfidfTable.transpose() #transpose rows and columns to document and information
    tfidfTableDic = tfidfTable.to_dict() #create a dictionary with the tfidf-values
    tfidfTableDic = filterTfidfDictionary(tfidfTableDic, 0.02, "more") #use the previously defined function to filter the tf-idf dictionary, include only words with a tf-idf value higher than 0.02
    

    #tfidfTableDic = json.load(open("/Users/romanovienna/Dropbox/6.Teaching_New/BUILDING_MEMEX_COURSE/_memex_sandbox/_data/results_tfidf_publications.dataJson"))

    # PART 4: generating wordclouds
    print("\tgenerating wordclouds...") #print to inform about the processing
    wc = WordCloud(width=1000, height=600, background_color="white", random_state=2,
                relative_scaling=0.5, #color_func=lambda *args, **kwargs: (179,0,0)) # single color
                #colormap="copper") # Oranges, Reds, YlOrBr, YlOrRd, OrRd; # copper
                colormap="gray") # binary, gray
                # https://matplotlib.org/3.1.1/gallery/color/colormap_reference.html
                #define the settings for your wordcloud, choose your preferred colours

    counter = len(tfidfTableDic) #count the number of dictionaries with the tfidf-values
    citeKeys = list(tfidfTableDic.keys()) #sort the citationKeys
    random.shuffle(citeKeys) #shuffle your citationKeys

    for citeKey in citeKeys: #loop through your citationKeys
        savePath = functions.generatePublPath(pathToMemex, citeKey) #take the filepath generated by one of our previous function
        savePath = os.path.join(savePath, "%s_wCloud.jpg" % citeKey) #save the wordcloud as jpg-file

        if not os.path.isfile(savePath): #check if the jpg-file exists already, if not:
            wc.generate_from_frequencies(tfidfTableDic[citeKey]) #generate the wordcloud
            # plotting
            plt.imshow(wc, interpolation="bilinear") #plot the wordcloud
            plt.axis("off")
            #plt.show() # this line shows the plot
            plt.savefig(savePath, dpi=200, bbox_inches='tight') #save the wordcloud

            print("\t%s (%d left...)" % (citeKey, counter)) #print how many wordclouds are left to be saved
            counter -= 1 #subtract the created file
        
        else:
            print("\t%s --- already done" % (citeKey)) #print that a jpg-file with the wordcloud has already been saved
            counter -= 1 #subtract the already existing file 

        # WordCloud:
        #   colormap: https://matplotlib.org/3.3.3/tutorials/colors/colormaps.html
        #   font_path="./fonts/Baskerville.ttc" (path to where your font is)
        #   Documentation: https://amueller.github.io/word_cloud/index.html
        #input("Check the plot!")

###########################################################
# PROCESS ALL RECORDS: WITH PROMPT ########################
###########################################################

print("""
============= GENERATING WORDCLOUDS ===============
   Type "YES", if you want to regenerate new files;
Old files will be deleted and new ones regenerated;
Press `Enter` to continue generating missing files.
===================================================
""") #print a statement so that the user can decide whether they want to regenerate existing files as well
response = input()

if response.lower() == "yes": #if they want to regenerate existing files as well
    print("Deleting existing files...") #print a statement that informs about this process
    functions.removeFilesOfType(settings["path_to_memex"], "_wCloud.jpg") #remove these old files
    print("Generating new files...") #print a statement that keeps the user updated
    generateTfIdfWordClouds(settings["path_to_memex"]) #create the new jpg-files with the wordclouds
else: #if they only want to generate missing files
    print("Getting back to generating missing files...") #print a statement that keeps the user updated
    generateTfIdfWordClouds(settings["path_to_memex"]) #create the missing jpg-files with the wordclouds