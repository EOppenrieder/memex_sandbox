import functions
import json
import re
import yaml
from datetime import datetime

settingsFile = "settings.yml"
settings = yaml.safe_load(open(settingsFile))
memexPath = settings["path_to_memex"]

import functions
import yaml, json, re, os
settingsFile = "settings.yml"
settings = yaml.safe_load(open(settingsFile))
memexPath = settings["path_to_memex"]

def search(searchArgument):
    targetFiles = functions.dicOfRelevantFiles(memexPath, ".json")  #get all the json files
    citeKeys = list(targetFiles.keys()) #list of the citekeys    
    results = {}        
    for citeKey in citeKeys:    #loop through all the keys
        docData = json.load(open(targetFiles[citeKey], "r", encoding="utf8"))   #load the respective json file with the ocr results        
        for k, v in docData.items():    #keys = page numbers values = text
            #docData[k] ["timestamp"] = datetime.now 
            if searchArgument in v:      #if the search Argument is in the page
                matchCounter = len(re.findall(searchArgument, v))    #count how often                          
                if not citeKey in results.keys():   #creates an empty dict only if there isnt already one                           
                    results[citeKey] = {}                
                results[citeKey][k] = {}            #creates sub-dict with the page number as key
                results[citeKey][k]["matches"] = matchCounter   #at the key matches the number of matches                 pagePath = os.path.join(functions.generatePublPath(memexPath, citeKey), "pages//", k, ".html")  #creates the path to the html file for the page
                
                pagePath = os.path.join(functions.generatePublPath(memexPath, citeKey), "pages//", k + ".html")
                results[citeKey][k]["pathToPage"] = pagePath
                results[citeKey][k]["result"] = v   #adds the ocred text to the dict    

    with open("search.txt", 'w', encoding='utf8') as f9:    #saves it into a file too
        json.dump(results, f9, sort_keys=True, indent=4, ensure_ascii=False)    
    return(results)

def createResultsPage(results, searchArgument):
        # load page template
        with open(settings["template_search"], "r", encoding="utf8") as ft:
            template = ft.read()

        pageTemp = template
        pageTemp = pageTemp.replace("@SEARCHARGUMENT@", searchArgument)

        content = ""
        
        for k, v in results.items():            
            content = content + "\n" + '<button class="collapsible">@CITEKEY@</button> <div class="content"> <ul>'.replace("@CITEKEY@", k + " (%d Pages with results)" %len(results[k].keys()))            
            for key, val in v.items():
                element = '<li><b><hr>(pdfPage: @PDFPAGE@)</b><hr> <span class='"searchResult"'>@SEARCHARGUMENT@</span><br> <hr> <a href="@PAGELINK@"><i>go to the original page...</i></a> </li>'.replace("@SEARCHARGUMENT@", searchArgument)
                element = element.replace("@PDFPAGE@", key)
                element = element.replace("@PAGELINK@", val["pathToPage"])

                content = content + element
            content = content + "</ul></div>"
                            

        pageTemp = pageTemp.replace("@buttons@", content)

        with open("search.html", "w", encoding="utf8") as f9:
            f9.write(pageTemp)

results = search("congress")
createResultsPage(results, "congress")



#take a string as argument
#def searchFunction(searchword, ocrFiles):
 #   searchword = input("Please enter a regular expression: ")

    ##load OCR results
  #  ocrFiles = functions.dicOfRelevantFiles(memexPath, ".json")
   # citeKeys = list(ocrFiles.keys())
    #docData = json.load(open(ocrFiles[citeKeys], "r", encoding="utf8"))

    #OuterdicOfMatches = {}
    #with k = citeKey and v = dictionary of matches, v = timestamp and v = searchword
    # InnerdicofMatches = {}
    #with k = pageNumbers and v = number of matches + search result

   # for citeKeys, searchword in ocrFiles.items():
    #    dicOfMatches = {} #dicOfMatches[citeKeys]
     #   for pages, val in dicOfMatches.items():
      #      if searchword in dicOfMatches:
       #         dicOfMatches [citeKeys] [pages] = searchword

   # print(dicOfMatches)

#searchFunction(searchword, ocrFiles)

#def search():    ## load OCR results
 #   ocrFiles = functions.dicOfRelevantFiles(memexPath, ".json")   
  #  citeKeys = list(ocrFiles.keys())    
   # word = input("Please enter a word: ")    
    #dicOfMatches = {}       # dictionary with citeKeys as value, matches as value    
    #for citeKeys, word in ocrFiles.items():   
     #   val = json.load(open(ocrFiles[citeKeys],"r", encoding= "utf8"))         
      #  for word in val:
       #     if word in val:
        #        dicOfMatches[citeKeys]  = word 
         #   else: 
          #      dicOfMatches[citeKeys] = "notinthepage"        
    #print (dicOfMatches)   # def searchDic (dic, word):

#search() 
 
 #   searchDic = {}    
  #  for k,v in dic.items():      # for citekeys
   #     searchDic[v]={}
    #    for key, val in v:
     #       if word in val: 
      #          searchDic[k][key] = val
    #return(searchDic)    #searchedDic = {}
   # searchedDic = functions.searchDic(ocrFiles, word)  #  with open("searchresults.txt", 'w', encoding='utf8') as f9:              ## save it into a textfile; avoid extension .json;
   #     json.dump(searchedDic, f9, sort_keys=True, indent=4, ensure_ascii=False)search()