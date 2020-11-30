import os, shutil, re
import yaml

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "./settings.yml" #to define your settings file
settings = yaml.load(open(settingsFile), Loader = yaml.FullLoader) #to define the settings you need 

memexPath = settings["path_to_memex"] #to define your path

###########################################################
# FUNCTIONS ###############################################
###########################################################

# load bibTex Data into a dictionary
def loadBib(bibTexFile):

    bibDic = {} #create an empty dictionary
    

    with open(bibTexFile, "r", encoding="utf8") as f1: #open your BibTex file
        records = f1.read().split("\n@") #read your file as one big string and split it into single records

        for record in records[1:]: #loop through each of these records except for the first one 
            # let process ONLY those records that have PDFs
            if ".pdf" in record.lower(): #so that there won't be any issues with case sensitivity
                completeRecord = "\n@" + record #add the @sign to each of the records to get a usable full record

                record = record.strip().split("\n")[:-1] ##get rid of the white spaces and split each record into key-value-pairs (except for the closing curly bracket)

                rType = record[0].split("{")[0].strip() #split the first element of the list to get the type of the record
                rCite = record[0].split("{")[1].strip().replace(",", "") #split the first element to get the Citation Key

                bibDic[rCite] = {} #specify your empty dictionary
                bibDic[rCite]["rCite"] = rCite #add a record into your dictionary using citationKey as a key value
                bibDic[rCite]["rType"] = rType #add recordType into the newly created record
                bibDic[rCite]["complete"] = completeRecord #add the complete data for your record
                #now you have a single-record dictionary for each of your records
                for r in record[1:]: #loop through the rest of your single record
                    key = r.split("=")[0].strip() #get the key of each key-value-pair of your single record
                    val = r.split("=")[1].strip() #get the value of each key-value-pair of your single record
                    val = re.sub("^\{|\},?", "", val) #get rid of unwanted characters

                    bibDic[rCite][key] = val #connect the key-value-pairs

                    # fix the path to PDF
                    if key == "file": #check for the file-key in your record
                        if ";" in val: #check if there are two paths
                            #print(val)
                            temp = val.split(";") #create a new variable with the both paths

                            for t in temp:
                                if ".pdf" in t: #check if one path ends with a .pdf-extension
                                    val = t #assign that path to the value for the key "file"

                            bibDic[rCite][key] = val #connect the key-value-pairs

    print("="*80) #print a line of equal signs
    print("NUMBER OF RECORDS IN BIBLIGORAPHY: %d" % len(bibDic)) #print the number of records in your dictionary
    print("="*80) #print a line of equal signs
    return(bibDic) #return your dictionary

# generate path from bibtex code, and create a folder, if does not exist;
# if the code is `SavantMuslims2017`, the path will be pathToMemex+`/s/sa/SavantMuslims2017/`
def generatePublPath(pathToMemex, bibTexCode): #define a function with the needed parameters
    temp = bibTexCode.lower() #create a temporary variable for your bibTexCode, which is your citation key
    directory = os.path.join(pathToMemex, temp[0], temp[:2], bibTexCode) #generate a unique path
    return(directory) #return that path

# process a single bibliographical record: 1) create its unique path; 2) save a bib file; 3) save PDF file 
def processBibRecord(pathToMemex, bibRecDict): #define a function with the needed parameters
    tempPath = generatePublPath(pathToMemex, bibRecDict["rCite"]) #generate a unique path

    print("="*80) #print a line of equal signs
    print("%s :: %s" % (bibRecDict["rCite"], tempPath)) #print that unique path
    print("="*80) #print a line of equal signs

    if not os.path.exists(tempPath): #check if that path exists
        os.makedirs(tempPath) #create the path if it does not exist

        bibFilePath = os.path.join(tempPath, "%s.bib" % bibRecDict["rCite"]) #create a path for your bibliographical record
        with open(bibFilePath, "w", encoding="utf8") as f9: #create a bibfile with your bibliographical record
            f9.write(bibRecDict["complete"]) #insert the complete bibliographical record

        pdfFileSRC = bibRecDict["file"] #create a variable for the path to your pdf-File
        pdfFileSRC = pdfFileSRC.replace ("\\:", ":") #get rid of unnecessary backslashes
        pdfFileDST = os.path.join(tempPath, "%s.pdf" % bibRecDict["rCite"]) #create a unique path for your pdf-File
        if not os.path.isfile(pdfFileDST): # this is to avoid copying that had been already copied.
            shutil.copyfile(pdfFileSRC, pdfFileDST) #copy your file from the old destination to the new one


###########################################################
# PROCESS ALL RECORDS #####################################
###########################################################

def processAllRecords(bibData): #define a function to process all your bibliographical records
    for k,v in bibData.items(): #take each record
        processBibRecord(memexPath, v) #process each of these records with the above generated function

bibData = loadBib(settings["bib_all"]) #get the data from all bibliographical records
processAllRecords(bibData) #process the data

print("Done!")