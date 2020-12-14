import pdf2image
import os
import pytesseract
import functions
import RemoveComments
import PyPDF2
import json
import yaml

settingsFile = "./settings.yml"
settings = yaml.load(open(settingsFile), Loader = yaml.FullLoader)

memexPath = settings["path_to_memex"]

def ocrPublication(pathToMemex, citationKey, language):
    #citationKey = "baumgart_wiener_2015"
    #language = "eng"
    publPath = functions.generatePublPath(pathToMemex, citationKey)
    pdfFile  = os.path.join(publPath, citationKey + ".pdf")
    jsonFile = os.path.join(publPath, citationKey + ".json")
    saveToPath = os.path.join(publPath, "pages")

    pdfFileTemp = RemoveComments.removeCommentsFromPDF(pdfFile)

    if not os.path.isfile(jsonFile):
        if not os.path.exists(saveToPath):
            os.makedirs(saveToPath)
        
        print("\t>>> OCR-ing: %s" % citationKey)

        textResults = {}
        images = pdf2image.convert_from_path(pdfFileTemp)
        pageTotal = len(images)
        pageCount = 1
        for image in images:
            image = image.convert('1')
            finalPath = os.path.join(saveToPath, "%04d.png" % pageCount)
            image.save(finalPath, optimize=True, quality=10)

            text = pytesseract.image_to_string(image, lang="eng")
            textResults["%04d" % pageCount] = text

            print("\t\t%04d/%04d pages" % (pageCount, pageTotal))
            pageCount += 1

        with open(jsonFile, 'w', encoding='utf8') as f9:
            json.dump(textResults, f9, sort_keys=True, indent=4, ensure_ascii=False)
    
    else:
        print("\t>>> %s has already been OCR-ed..." % citationKey)

    os.remove(pdfFileTemp)
#ocrPublication("C:\\Users\\elias\\memex_sandbox\\_data", "baumgart_wiener_2015", language="eng")

#############
######## ALL FILES
#############

bibData = functions.loadBib(settings["bib_all"])

#def getLang(bibData):    
 #   tempDic = {}    
  #  for k,v in bibData.items():        
   #     if v["language"] in tempDic:
    #        tempDic[v["language"]] +=1        
     #   else:
      #      tempDic[v["language"]] = 1    
            
       # results = []    
        
    #for k,v in tempDic.items():
     #   result = "%010d\t%s" % (v, k)
      #  results.append(result)    
       # results = sorted(results, reverse=True)
        #results = "\n".join(results)    
        #with open("lang_analysis.txt", "w", encoding="utf8") as f9:
         #   f9.write(results)
#getLang(bibData)

def processAllFiles(pathToMemex):
    bibData = functions.loadBib(settings["bib_all"])    #loads the bib file    
    languages = yaml.load(open("language_keys.yml"), Loader = yaml.FullLoader)   #loads the languages from the yaml file    
    for k,v in bibData.items(): 
        try:    #goes through the bib file        
            if v["language"] in languages:        #if the language is in the yaml file
                tempLang = languages[v["language"]]   #take the proper OCR abreviation for the language
            elif v["language"] not in languages:      #if not print a warning
                print(v["language"]+"is not in the "+languages+"file, please add. Will try with english as default")
                tempLang = "eng" #default = eng
        except:   
            tempLang = "eng" #default        
            print(tempLang)    
        ocrPublication(pathToMemex, k, languages)  


#def processAllRecords(bibData):
    #for k,v in bibData.items():
        # 1. create folders, copy files
       # functions.processBibRecord(memexPath, v)
        # 2. OCR the file
        #language = identifyLanguage(v, "eng")
        #ocrPublication(memexPath, v["rCite"], language)
#bibData = functions.loadBib(settings["bib_all"])
#processAllRecords(bibData)
 

processAllFiles(memexPath)
        