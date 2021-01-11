import os, json

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions
import LoadYml
import generate
import bibText
import dic

###########################################################
# VARIABLES ###############################################
###########################################################

settings = LoadYml.loadYmlSettings("settings.yml") #loads our settings file

###########################################################
# FUNCTIONS ###############################################
###########################################################

# generate interface for the publication
def generatePublicationInterface(citeKey, pathToBibFile): #defines a function that takes the citation key and the path to a .bib-file as arguments
    print("="*80) #prints a line of equals signs
    print(citeKey) #prints the citation key

    jsonFile = pathToBibFile.replace(".bib", ".json") #creates a variable for the json-File
    with open(jsonFile, encoding="utf8") as jsonData: #opens the json-File with the OCRed text
        ocred = json.load(jsonData) #loads the OCRed data
        pNums = ocred.keys() #sorts the data according to the keys, i.e. page numbers

        pageDic = generate.generatePageLinks(pNums) #loads the function which generates links to all pages in a publication

        # load page template
        with open(settings["template_page"], "r", encoding="utf8") as ft:
            template = ft.read() #loads the page template

        # load individual bib record
        bibFile = pathToBibFile #takes the pathToBibFile
        bibDic = functions.loadBib(bibFile) #loads the loadBib-function which loads the bibTex data into a dictionary
        bibForHTML = bibText.prettifyBib(bibDic[citeKey]["complete"]) #loads the prettifyBib-function to make the bib record more readable (taking the complete bib record)

        orderedPages = list(pageDic.keys()) #creates a list of keys to get all page numbers

        for o in range(0, len(orderedPages)): #loops through the pages
            #print(o)
            k = orderedPages[o] #takes the number of the page as key
            v = pageDic[orderedPages[o]] #takes the links to the other pages as value

            pageTemp = template #assigns the page template to a temporary variable
            pageTemp = pageTemp.replace("@PAGELINKS@", v) #replaces the Pagelinks item with the links to the other pages
            pageTemp = pageTemp.replace("@PATHTOFILE@", "") #replaces the Pathtofile item with a blank
            pageTemp = pageTemp.replace("@CITATIONKEY@", citeKey) #replaces the Citationkey item with the citation key

            if k != "DETAILS": #if the page is not the details page
                mainElement = '<img src="@PAGEFILE@" width="100%" alt="">'.replace("@PAGEFILE@", "%s.png" % k) #takes the .png-file of the OCRed text of this page
                pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement) #replaces the Mainelement item with the .png-file of the OCRed text
                pageTemp = pageTemp.replace("@OCREDCONTENT@", ocred[k].replace("\n", "<br>")) #replaces the OCRedContent item with the OCRed text
            else: #if the page is the details page
                mainElement = bibForHTML.replace("\n", "<br> ") #makes the description more html-friendly
                mainElement = '<div class="bib">%s</div>' % mainElement #takes the bibliographical information
                mainElement += '\n<img src="wordcloud.jpg" width="100%" alt="wordcloud">' #adds a wordcloud image
                pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement) #replaces the MainElement item with the bibliographical information and the wordcloud image
                pageTemp = pageTemp.replace("@OCREDCONTENT@", "") #replaces the OCRedContent item with a blank

            # @NEXTPAGEHTML@ and @PREVIOUSPAGEHTML@
            if k == "DETAILS": #if the page is the Details page
                nextPage = "0001.html" #the next page is the first page of the record
                prevPage = "" #there is no previous page
            elif k == "0001": #if the page is the first page of the record
                nextPage = "0002.html" #the next page is the second page of the record
                prevPage = "DETAILS.html" #the previous page is the Details page
            elif o == len(orderedPages)-1: #if the page is the last page of the record
                nextPage = "" #there is no next page
                prevPage = orderedPages[o-1] + ".html" #the previous page is the penultimate page of the record
            else: #for all other pages
                nextPage = orderedPages[o+1] + ".html" #the next page is the page behind in the record
                prevPage = orderedPages[o-1] + ".html" #the previous page is the page before in the record

            pageTemp = pageTemp.replace("@NEXTPAGEHTML@", nextPage) #replaces the Nextpagehtml item with a link to the page assigned in the lines before
            pageTemp = pageTemp.replace("@PREVIOUSPAGEHTML@", prevPage) #replaces the Previouspagehtml item with  a link to the page assigned in the lines before

            pagePath = os.path.join(pathToBibFile.replace(citeKey+".bib", ""), "pages", "%s.html" % k) #creates a filepath to each page in the pages-folder of each publication
            with open(pagePath, "w", encoding="utf8") as f9:
                f9.write(pageTemp) #creates and saves each page in that pages folder

# generate the INDEX and the CONTENTS pages
def generateMemexStartingPages(pathToMemex): #creates a definition to generate the INDEX and the CONTENTS pages
    # load index template
    with open(settings["template_index"], "r", encoding="utf8") as ft:
        template = ft.read() #loads the template_index.html-file

    # add index.html
    with open(settings["content_index"], "r", encoding="utf8") as fi:
        indexData = fi.read() #loads the content_index.html-file
        with open(os.path.join(pathToMemex, "index.html"), "w", encoding="utf8") as f9: #creates an index.html-file
            f9.write(template.replace("@MAINCONTENT@", indexData)) #replaces the Maincontent-item with the actual indexData

    # load bibliographical data for processing
    publicationDic = {} # key = citationKey; value = recordDic

    for subdir, dirs, files in os.walk(pathToMemex): #loops through all our folders, subfolders and files
        for file in files: #takes each file
            if file.endswith(".bib"): #takes all bib-Files
                pathWhereBibIs = os.path.join(subdir, file) #takes the path to the bib-Files
                tempDic = functions.loadBib(pathWhereBibIs) #creates a temporary dictionary with the bibliographical data from our bibFiles
                publicationDic.update(tempDic) #adds the content from that temporary dictionary into our publication dictionary so that all records are stored there

    # generate data for the main CONTENTS
    singleItemTemplate = '<li><a href="@RELATIVEPATH@/pages/DETAILS.html">[@CITATIONKEY@]</a> @AUTHOROREDITOR@ (@DATE@) - <i>@TITLE@</i></li>' #takes the template for a single item
    contentsList = [] #creates an empty list

    for citeKey,bibRecord in publicationDic.items(): #loops through the publication dictionary
        relativePath = functions.generatePublPath(pathToMemex, citeKey).replace(pathToMemex, "") #takes the relative path to our records, removes the citation Key

        authorOrEditor = "[No data]" #creates a variable for the author or editor of the record 
        if "editor" in bibRecord: #searches for the editor in the record
            authorOrEditor = bibRecord["editor"] #assigns the editor to the variable
        if "author" in bibRecord: #searches for the author in the record
            authorOrEditor = bibRecord["author"] #assigns the author to the record

        date = bibRecord["year"][:4] #creates a variable for the date of the record which takes only the first four digits not to get any months or days

        title = bibRecord["title"] #creates a variable for the title of the record

        # forming a record
        recordToAdd = singleItemTemplate #takes the singleItem-template to form each record
        recordToAdd = recordToAdd.replace("@RELATIVEPATH@", relativePath) #assigns the relative path of the record
        recordToAdd = recordToAdd.replace("@CITATIONKEY@", citeKey) #assigns the citation key of the record
        recordToAdd = recordToAdd.replace("@AUTHOROREDITOR@", authorOrEditor) #assigns the author or editor of the record
        recordToAdd = recordToAdd.replace("@DATE@", date) #assigns the date of the record
        recordToAdd = recordToAdd.replace("@TITLE@", title) #assigns the title of the record

        recordToAdd = recordToAdd.replace("{", "").replace("}", "") #removes curly brackets to make the record more readable

        contentsList.append(recordToAdd) #adds the record to the content list

    contents = "\n<ul>\n%s\n</ul>" % "\n".join(sorted(contentsList)) #assigns the sorted content list, adds an opening and a closing tag
    mainContent = "<h1>CONTENTS of MEMEX</h1>\n\n" + contents #adds a header and assigns the content

    # save the CONTENTS page
    with open(os.path.join(pathToMemex, "contents.html"), "w", encoding="utf8") as f9: #creates and saves the content page
        f9.write(template.replace("@MAINCONTENT@", mainContent)) #replaces the MainContent-Item in the template with the actual mainContent we have just created

###########################################################
# FUNCTIONS TESTING #######################################
###########################################################

#generatePublicationInterface("AshkenaziHoly2014", "./_memex_sandbox/_data/a/as/AshkenaziHoly2014/AshkenaziHoly2014.bib") #tests our function for one single record

###########################################################
# PROCESS ALL RECORDS: ANOTHER APPROACH ###################
###########################################################

# Until now we have been processing our publications through
# out bibTeX file; we can also consider a slightly different
# approach that will be more flexible.

def processAllRecords(pathToMemex): #definition to process all our records
    files = dic.dicOfRelevantFiles(pathToMemex, ".bib") #takes the dictionary with our bibFiles
    for citeKey, pathToBibFile in files.items(): #loops through all the bibFiles
        #print(citeKey)
        generatePublicationInterface(citeKey, pathToBibFile) #generates the interfaces for all bibFiles
    generateMemexStartingPages(pathToMemex) #adds the information for each record to our contents-page

processAllRecords(settings["path_to_memex"]) #processes all the records

# HOMEWORK:
# - give all functions: task - to write a function that process everything
# - give a half-written TOC function which creates an index file;
#   they will need to finish it by adding generation of the TOC file