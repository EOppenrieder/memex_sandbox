#wordcloud definition
#we need the path to save file and a dictionary of tf-idf terms
#you can always use the file with tf-idf values that you generated before, although you might want to change max_df and min_df parameters 

from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import functions
import yaml
import json

settingsFile = "settings.yml"
settings = yaml.safe_load(open(settingsFile))
memexPath = settings["path_to_memex"]
#citationKey = conze_konzertierte_2015

#publPath = functions.generatePublPath(memexPath, conze_konzertierte_2015)
#savePath = os.path.join(publPath, conze_konzertierte_2015 + ".jpg")
#savePath = "C:\\Users\\elias\\memex_sandbox\\_data\\c\\co\\conze_konzertierte_2015" + ".jpg"
#jsonFile = pathToBibFile.replace(".bib", ".json") #creates a variable for the json-File
 #   with open(jsonFile, encoding="utf8") as jsonData: #opens the json-File with the OCRed text
  #      ocred = json.load(jsonData) #loads the OCRed data
   #     pNums = ocred.keys()

#ocrFiles = functions.dicOfRelevantFiles(memexPath, ".json")   
#citeKeys = list(ocrFiles.keys())


#savePath =  os.path.join(memexPath,"wordcloud" + ".jpg")

#tfIdfDic = json.load(open("C:\\Users\\elias\\memex_sandbox\\tfidfTableDic_filtered.txt", "r", encoding = "utf8"))
#print(tfidfDic)
def createWordCloud(savePath, tfIdfDic):
    wc = WordCloud(width=1000, height=600, background_color="white", random_state=2,
                   relative_scaling=0.5, colormap="gray") 
    wc.generate_from_frequencies(tfIdfDic)
    # plotting
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show() # this line will show the plot
    plt.savefig(savePath, dpi=200, bbox_inches='tight')
    
def createAll(filename):
    docData = json.load(open(filename, "r", encoding="utf8"))

    for k, v in docData.items():
        savePath = functions.generatePublPath(memexPath, k)
        savePath = savePath + "\\" + k
        if v:
            createWordCloud(savePath, v)

createAll("tfidfTableDic_filtered.txt")


#def createWordCloud(savePath, tfIdfDic):
    #tfIdfDic = "tfidfTableDic_filtered_refined.txt"
    #with open(temp, encoding="utf8") as jsonData:
     #       tfIdfDic = json.load(jsonData)
    #savePath = memexPath + ".jpg"
 #   wc = WordCloud(width=1000, height=600, background_color="white", random_state=2,
  #                 relative_scaling=0.5, colormap="gray") 
   # wc.generate_from_frequencies(tfIdfDic)
    # plotting
    #plt.imshow(wc, interpolation="bilinear")
    #plt.axis("off")
    #plt.show() # this line will show the plot
    #plt.savefig(savePath, dpi=200, bbox_inches='tight')

#createWordCloud(savePath, tfIdfDic)