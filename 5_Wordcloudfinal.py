# NEW LIBRARIES
import pandas as pd
from sklearn.feature_extraction.text import (CountVectorizer, TfidfTransformer)
from sklearn.metrics.pairwise import cosine_similarity

import os, json, re, random
import yaml, sys

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "settings.yml"
settings = yaml.safe_load(open(settingsFile))

###########################################################
# MAIN FUNCTIONS ##########################################
###########################################################

from wordcloud import WordCloud
import matplotlib.pyplot as plt

def generateWordCloud(citeKey, pathToFile):
    # aggregate dictionary
    data = json.load(open(pathToFile))
    dataNew = {}
    for page,pageDic in data.items():
        for term, tfIdf in pageDic.items():
            if term in dataNew:
                dataNew[term] += tfIdf
            else:
                dataNew[term]  = tfIdf

def filterTfidfDictionary(dictionary, threshold, lessOrMore):
    dictionaryFilt = {}
    for item1, citeKeyDist in dictionary.items():
        dictionaryFilt[item1] = {}
        for item2, value in citeKeyDist.items():
            if lessOrMore == "less":
                if value <= threshold:
                    if item1 != item2:
                        dictionaryFilt[item1][item2] = value
            elif lessOrMore == "more":
                if value >= threshold:
                    if item1 != item2:
                        dictionaryFilt[item1][item2] = value
            else:
                sys.exit("`lessOrMore` parameter must be `less` or `more`")

        if dictionaryFilt[item1] == {}:
            dictionaryFilt.pop(item1)
    return(dictionaryFilt)


def generateTfIdfWordClouds(pathToMemex):
    # PART 1: loading OCR files into a corpus
    ocrFiles = functions.dicOfRelevantFiles(pathToMemex, ".json")
    citeKeys = list(ocrFiles.keys())#[:500]

    print("\taggregating texts into documents...")
    docList   = []
    docIdList = []

    for citeKey in citeKeys:
        docData = json.load(open(ocrFiles[citeKey], "r", encoding="utf8"))
        
        docId = citeKey
        doc   = " ".join(docData.values())

        # clean doc
        doc = re.sub(r'(\w)-\n(\w)', r'\1\2', doc)
        doc = re.sub('\W+', ' ', doc)
        doc = re.sub('_+', ' ', doc)
        doc = re.sub('\d+', ' ', doc)
        doc = re.sub(' +', ' ', doc)

        # update lists
        docList.append(doc)
        docIdList.append(docId)

    print("\t%d documents generated..." % len(docList))

    # PART 2: calculate tfidf for all loaded publications and distances
    print("\tgenerating tfidf matrix & distances...")
    stopWords = functions.loadMultiLingualStopWords(["deu", "eng", "fre"])
    vectorizer = CountVectorizer(ngram_range=(1,1), min_df=2, max_df=0.5, stop_words = stopWords) 
    countVectorized = vectorizer.fit_transform(docList)
    tfidfTransformer = TfidfTransformer(smooth_idf=True, use_idf=True)
    vectorized = tfidfTransformer.fit_transform(countVectorized) # generates a sparse matrix

    print("\tconverting and filtering tfidf data...")
    tfidfTable = pd.DataFrame(vectorized.toarray(), index=docIdList, columns=vectorizer.get_feature_names())
    tfidfTable = tfidfTable.transpose()
    tfidfTableDic = tfidfTable.to_dict()
    tfidfTableDic = filterTfidfDictionary(tfidfTableDic, 0.03, "more")
    

    #tfidfTableDic = json.load(open("/Users/romanovienna/Dropbox/6.Teaching_New/BUILDING_MEMEX_COURSE/_memex_sandbox/_data/results_tfidf_publications.dataJson"))

    # PART 4: generating wordclouds
    print("\tgenerating wordclouds...")
    wc = WordCloud(width=1000, height=600, background_color="white", random_state=2,
                relative_scaling=0.5, #color_func=lambda *args, **kwargs: (179,0,0)) # single color
                #colormap="copper") # Oranges, Reds, YlOrBr, YlOrRd, OrRd; # copper
                colormap="autumn") # binary, gray
                # https://matplotlib.org/3.1.1/gallery/color/colormap_reference.html

    counter = len(tfidfTableDic)
    citeKeys = list(tfidfTableDic.keys())
    random.shuffle(citeKeys)

    for citeKey in citeKeys:
        savePath = functions.generatePublPath(pathToMemex, citeKey)
        savePath = os.path.join(savePath, "%s_wCloud.jpg" % citeKey)

        if not os.path.isfile(savePath):
            wc.generate_from_frequencies(tfidfTableDic[citeKey])
            # plotting
            plt.imshow(wc, interpolation="bilinear")
            plt.axis("off")
            #plt.show() # this line shows the plot
            plt.savefig(savePath, dpi=200, bbox_inches='tight')

            print("\t%s (%d left...)" % (citeKey, counter))
            counter -= 1
        
        else:
            print("\t%s --- already done" % (citeKey))
            counter -= 1

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
""")
response = input()

if response.lower() == "yes":
    print("Deleting existing files...")
    functions.removeFilesOfType(settings["path_to_memex"], "_wCloud.jpg")
    print("Generating new files...")
    generateTfIdfWordClouds(settings["path_to_memex"])
else:
    print("Getting back to generating missing files...")
    generateTfIdfWordClouds(settings["path_to_memex"])