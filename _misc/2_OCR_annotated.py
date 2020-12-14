# NEW LIBRARIES
import pdf2image    # extracts images from PDF
import pytesseract  # interacts with Tesseract, which extracts text from images
import PyPDF2       # cleans PDFs

import os, yaml, json, random #imports a few more libraries we need for this script

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions # imports our functions file with various previous functions

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "settings.yml" #defines our settings file
settings = yaml.load(open(settingsFile)) #loads our settings file

memexPath = settings["path_to_memex"] #defines the path for our memex
langKeys = yaml.load(open(settings["language_keys"])) #defines the settings for our language keys

###########################################################
# TRICKY FUNCTIONS ########################################
###########################################################

# the function creates a temporary copy of a PDF file
# with comments and highlights removed from it; it creates
# a clean copy of a PDF suitable for OCR-nig 
def removeCommentsFromPDF(pathToPdf):
    with open(pathToPdf, 'rb') as pdf_obj: #opens a pdf in binary mode
        pdf = PyPDF2.PdfFileReader(pdf_obj) #defines that the PDF is opened with the PyPDF2 library
        out = PyPDF2.PdfFileWriter() #defines that a new cleaned PDF is created with the PyPDF2 library
        for page in pdf.pages: #loops through every page of the PDF
            out.addPage(page) #adds this page to the new cleaned PDF
            out.removeLinks() #removes links, comments, annotations
        tempPDF = pathToPdf.replace(".pdf", "_TEMP.pdf") #replaces the filename
        with open(tempPDF, 'wb') as f: #opens the new cleaned PDF in binary mode
            out.write(f) #creates the new cleaned PDF
    return(tempPDF) #returns the new cleaned PDF

# function OCR a PDF, saving each page as an image and
# saving OCR results into a JSON file
def ocrPublication(pathToMemex, citationKey, language):
    # generate and create necessary paths
    publPath = functions.generatePublPath(pathToMemex, citationKey) #generates the path to our PDF file
    pdfFile  = os.path.join(publPath, citationKey + ".pdf") #creates the path to the PDF file
    jsonFile = os.path.join(publPath, citationKey + ".json") # OCR results will be saved here
    saveToPath = os.path.join(publPath, "pages") # we will save processed images here

    # generate CLEAN pdf (necessary if you added highlights and comments to your PDFs)
    pdfFileTemp = removeCommentsFromPDF(pdfFile)

    # first we need to check whether this publication has been already processed
    if not os.path.isfile(jsonFile):
        # let's make sure that saveToPath also exists
        if not os.path.exists(saveToPath):
            os.makedirs(saveToPath)
        
        # start process images and extract text
        print("\t>>> OCR-ing: %s" % citationKey)

        textResults = {} #creates a dictionary
        images = pdf2image.convert_from_path(pdfFileTemp) #iterates through the pages
        pageTotal = len(images) #counts the length of the PDF
        pageCount = 1 #lets the count start with 1
        for image in images: #loops through the images
            image = image.convert('1') # binarizes image, reducing its size
            finalPath = os.path.join(saveToPath, "%04d.png" % pageCount) #crates the path for your OCRed pages
            image.save(finalPath, optimize=True, quality=10) #saves the OCRed pages

            text = pytesseract.image_to_string(image, lang=language) #extracts the text from your images
            textResults["%04d" % pageCount] = text #saves the text into your dictionary

            print("\t\t%04d/%04d pages" % (pageCount, pageTotal)) #prints the progress of the OCRing process
            pageCount += 1 #keeps counting you pages

        with open(jsonFile, 'w', encoding='utf8') as f9: #creates a jsonFile for your OCRed text
            json.dump(textResults, f9, sort_keys=True, indent=4, ensure_ascii=False) #puts the OCRed text into the jsonFile 
    
    else: # in case JSON file already exists
        print("\t>>> %s has already been OCR-ed..." % citationKey) #shows that yozu have already created a jsonFile for that record

    os.remove(pdfFileTemp) #removes the temporary PDF file

def identifyLanguage(bibRecDict, fallBackLanguage): #defines a function to sort out the language of your record
    if "langid" in bibRecDict: #checks if there is a language key in the dictionary with your bibliography for a record
        try:
            language = langKeys[bibRecDict["langid"]] #tries to match the language ID with the tesseract language settings
            message = "\t>> Language has been successfuly identified: %s" % language #prints a message with the language name if the ID has been successfully matched
        except:
            message = "\t>> Language ID `%s` cannot be understood by Tesseract; fix it and retry\n" % bibRecDict["langid"] #tells you that the ID could not be matched with the Tesseract language settings
            message += "\t>> For now, trying `%s`..." % fallBackLanguage #tells you that it will use your default language
            language = fallBackLanguage #assigns the default language as language of that record
    else:
        message = "\t>> No data on the language of the publication" #tells you that there is no language key in the dictionary with your bibliography for a record
        message += "\t>> For now, trying `%s`..." % fallBackLanguage #tells you that it will use your default language
        language = fallBackLanguage #assigns the default language as language of that record
    print(message) #prints the messages
    return(language) #returns the language of that record

###########################################################
# FUNCTIONS TESTING #######################################
###########################################################

#ocrPublication("AbdurasulovMaking2020", "eng")

###########################################################
# PROCESS ALL RECORDS: APPROACH 1 #########################
###########################################################


def processAllRecords(bibData): #defines a functions to process all your records
    for k,v in bibData.items(): #loops through key-value-pairs in your bibData-dictionary
        # 1. create folders, copy files
        functions.processBibRecord(memexPath, v)
        # 2. OCR the file
        language = identifyLanguage(v, "eng")
        ocrPublication(memexPath, v["rCite"], language) #assigns the parameters to your previously defined function
bibData = functions.loadBib(settings["bib_all"]) #loads the file with your bibliography
processAllRecords(bibData) #processes all your records


###########################################################
# PROCESS ALL RECORDS: APPROACH 2 #########################
###########################################################

# Why this way? Our computers are now quite powerful; they
# often have multiple cores and we can take advantage of this;
# if we process our data in the manner coded below --- we shuffle
# our publications and process them in random order --- we can
# run multiple instances fo the same script and data will
# be produced in parallel. You can run as many instances as
# your machine allows (you need to check how many cores
# your machine has). Even running two scripts will cut
# processing time roughly in half.

def processAllRecords(bibData): #defines a functions to process all your records
    keys = list(bibData.keys()) #extracts the keys of your dictionary
    random.shuffle(keys) #shuffles the keys

    for key in keys: #randomly loops through the keys
        bibRecord = bibData[key] #chooses a random record to process

        # 1. create folders, copy files
        functions.processBibRecord(memexPath, bibRecord)

        # 2. OCR the file
        language = identifyLanguage(bibRecord, "eng")
        ocrPublication(memexPath, bibRecord["rCite"], language)


bibData = functions.loadBib(settings["bib_all"]) #loads the file with your bibliography
processAllRecords(bibData) #processes all your records