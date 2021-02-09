# NEW LIBRARIES
import pdf2image    # extracts images from PDF
import pytesseract  # interacts with Tesseract, which extracts text from images

import os, yaml, json, random

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "./settings.yml"
settings = yaml.load(open(settingsFile), Loader = yaml.FullLoader)

pathToMemex = settings["path_to_memex"]
langKeys = yaml.load(open(settings["language_keys"]), Loader= yaml.FullLoader)

###########################################################
# MAIN FUNCTIONS ##########################################
###########################################################

# function OCR a PDF, saving each page as an image and
# saving OCR results into a JSON file
def ocrPublication(pathToMemex, citationKey, language):
    # generate and create necessary paths
    publPath = functions.generatePublPath(pathToMemex, citationKey)
    pdfFile  = os.path.join(publPath, citationKey + ".pdf")
    jsonFile = os.path.join(publPath, citationKey + ".json") # OCR results will be saved here
    saveToPath = os.path.join(publPath, "pages") # we will save processed images here

    # first we need to check whether this publication has been already processed
    if not os.path.isfile(jsonFile):
        # let's make sure that saveToPath also exists
        if not os.path.exists(saveToPath):
            os.makedirs(saveToPath)
        
        # start process images and extract text
        print("\t>>> OCR-ing: %s" % citationKey)

        textResults = {}
        images = pdf2image.convert_from_path(pdfFile)
        pageTotal = len(images)
        pageCount = 1
        
        for image in images:
            text = pytesseract.image_to_string(image, lang=language)
            textResults["%04d" % pageCount] = text

            image = image.convert('1') # binarizes image, reducing its size
            finalPath = os.path.join(saveToPath, "%04d.png" % pageCount)
            image.save(finalPath, optimize=True, quality=10)

            print("\t\t%04d/%04d pages" % (pageCount, pageTotal))
            pageCount += 1

        with open(jsonFile, 'w', encoding='utf8') as f9:
            json.dump(textResults, f9, sort_keys=True, indent=4, ensure_ascii=False)
        #else:
           # print("\t%d: the length of the publication exceeds current limit (%d)" % (pageTotal, pageLimit))
            #print("\tIncrease `page_limit` in settings to process this publication.")
    
    else: # in case JSON file already exists
        print("\t>>> %s has already been OCR-ed..." % citationKey)


def identifyLanguage(bibRecDict, fallBackLanguage):
    if "language" in bibRecDict:
        try:
            language = langKeys[bibRecDict["language"]]
            message = "\t>> Language has been successfuly identified: %s" % language
        except:
            message = "\t>> Language ID `%s` cannot be understood by Tesseract; fix it and retry\n" % bibRecDict["language"]
            message += "\t>> For now, trying `%s`..." % fallBackLanguage
            language = fallBackLanguage
    else:
        message = "\t>> No data on the language of the publication"
        message += "\t>> For now, trying `%s`..." % fallBackLanguage
        language = fallBackLanguage
    print(message)
    return(language)

#ocrPublication("C:\\Users\\elias\\memex_sandbox\\data", "svoger_political_2016", "eng")



def processAllRecords(bibData):
    keys = list(bibData.keys())
    random.shuffle(keys)

    for key in keys:
        bibRecord = bibData[key]

        functions.processBibRecord(pathToMemex, bibRecord)

        language = identifyLanguage(bibRecord, "eng")
        ocrPublication(pathToMemex, bibRecord["rCite"], language)


bibData = functions.loadBib(settings["bib_all"])
processAllRecords(bibData)

