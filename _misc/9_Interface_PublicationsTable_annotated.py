import os, json, unicodedata, yaml #import several libraries we need

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions #import the script with our previous functions

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "settings.yml" #define our settings file
settings = yaml.safe_load(open(settingsFile)) #load our settings file
memexPath = settings["path_to_memex"] #define the memex path

###########################################################
# MINI TEMPLATES ##########################################
###########################################################

connectionsTemplate = """
<button class="collapsible">Similar Texts (<i>tf-idf</i> + cosine similarity)</button>
  <div class="content">
  <ul>
    <li>
    <b>Sim*</b>: <i>cosine similarity</i>; 1 is a complete match, 0 — nothing similar;
    cosine similarity is calculated using <i>tf-idf</i> values of top keywords.</li>
  </ul>
<table id="publications" class="mainList">
<thead>
    <tr>
        <th>link</th>
        <th>Sim*</th>
        <th>Author(s), Year, Title, Pages</th>
    </tr>
</thead>
<tbody>
@CONNECTEDTEXTSTEMP@
</tbody>
</table>
</div>
"""
#define the connections template
ocrTemplate = """
<button class="collapsible">OCREDTEXT</button>
<div class="content">
  <div class="bib">
  @OCREDCONTENTTEMP@
  </div>
</div>
"""
#define the ocrTemnplate
generalTemplate = """
<button class="collapsible">@ELEMENTHEADER@</button>
<div class="content">
@ELEMENTCONTENT@
</div>
"""
#define the generalTemplate
###########################################################
# MINI FUNCTIONS ##########################################
###########################################################

import math
# a function for grouping pages into clusters of y number of pages
# x = number to round up; y = a multiple of the round-up-to number
def roundUp(x, y):
    result = int(math.ceil(x / y)) * y
    return(result)

# formats individual references to publications
def generateDoclLink(bibTexCode, pageVal, distance):
    pathToPubl = functions.generatePublPath(settings["path_to_memex"], bibTexCode) #take the bibTex-Code
    bib = functions.loadBib(os.path.join(pathToPubl, "%s.bib" % bibTexCode)) #load the bibTex-Code
    bib = bib[bibTexCode] #define a variable

    author = "N.d." #take no information on the author as default setting
    if "editor" in bib: #check if there is information about the editor
        author = bib["editor"] #insert it
    if "author" in bib: #check if there is information about the author
        author = bib["author"] #insert it

    reference = "%s (%s). <i>%s</i>" % (author, bib["year"][:4], bib["title"]) #take information about a publication and format it
    search = unicodedata.normalize('NFKD', reference).encode('ascii','ignore') #replace diacritical characters with their ascii equivalents
    search = " <div class='hidden'>%s</div>" % search #repeat the information and hide it

    if pageVal == 0: # link to the start of the publication
        htmlLink = os.path.join(pathToPubl.replace(settings["path_to_memex"], "../../../../"), "pages", "DETAILS.html") #create an html-link to the details page
        htmlLink = "<a href='%s'><i>read</i></a>" % (htmlLink) #add the link
        page = "" #define the variable page
        startPage = 0 #define the startPage as 0
    else:
        startPage = pageVal - 5 #define the startPage
        endPage   = pageVal #define the endPage
        if startPage == 0: #if the startPage is the details page
            startPage += 1 #add one to the startPage
        htmlLink = os.path.join(pathToPubl.replace(settings["path_to_memex"], "../../../../"), "pages", "%04d.html" % startPage) #create an html-link to the startPage
        htmlLink = "<a href='%s'><i>read</i></a>" % (htmlLink) #add the html-page
        page = ", pdfPp. %d-%d</i></a>" % (startPage, endPage) #add the pagecluster with startPage and endPage

    publicationInfo = reference + page + search #join the variables together
    publicationInfo = publicationInfo.replace("{", "").replace("}", "") #remove the curly brackets
    singleItemTemplate = '<tr><td>%s</td><td>%f</td><td data-order="%s%05d">%s</td></tr>' % (htmlLink, distance, bibTexCode, startPage, publicationInfo) #create a template for the indvidual item

    return(singleItemTemplate) #return this variable

def generateReferenceSimple(bibTexCode):
    pathToPubl = functions.generatePublPath(settings["path_to_memex"], bibTexCode) #take the bibTexCode
    bib = functions.loadBib(os.path.join(pathToPubl, "%s.bib" % bibTexCode)) #load the bibTexCode
    bib = bib[bibTexCode] #define a variable

    author = "N.d." #take no information on the author as default setting
    if "editor" in bib: #check if there is information about the editor
        author = bib["editor"] #insert it
    if "author" in bib: #check if there is information about the author
        author = bib["author"] #insert it

    reference = "%s (%s). <i>%s</i>" % (author, bib["year"][:4], bib["title"]) #take information about a publication and format it
    reference = reference.replace("{", "").replace("}", "") #remove the curly brackets
    return(reference) #return this variable

# convert json dictionary of connections into HTML format
def formatDistConnections(pathToMemex, distanceFile):
    print("Formatting distances data from `%s`..." % distanceFile)
    distanceFile = os.path.join(pathToMemex, distanceFile) #take the jsonFile with the cosine similarity-values
    distanceDict = json.load(open(distanceFile)) #load this jsonFile

    formattedHTML = {} #create an empty dictionary

    for doc1, doc1Dic in distanceDict.items(): #loop through the jsonFile
        formattedHTML[doc1] = [] #create an empty list
        for doc2, distance in doc1Dic.items(): #loop through the cosine similarity-values
            doc2 = doc2.split("_") #take the citeKey
            if len(doc2) == 1:
                tempVar = generateDoclLink(doc2[0], 0, distance) #create a temporary variable
            else:
                tempVar = generateDoclLink(doc2[0], int(doc2[1]), distance)

            formattedHTML[doc1].append(tempVar) #add the temporary variable
            #input(formattedHTML)
    print("\tdone!")
    return(formattedHTML) #return the variable

###########################################################
# MAIN FUNCTIONS ##########################################
###########################################################

publConnData = formatDistConnections(settings["path_to_memex"], settings["publ_cosDist"]) #define the settings for the similarity between publications
pageConnData = formatDistConnections(settings["path_to_memex"], settings["page_cosDist"]) #define the settings for the similarity between pageclusters

# generate interface for the publication and pages
def generatePublicationInterface(citeKey, pathToBibFile):
    print("="*80)
    print(citeKey) #print the citeKey of the publication

    jsonFile = pathToBibFile.replace(".bib", ".json") #take the bibFile
    with open(jsonFile, encoding="utf8") as jsonData:
        ocred = json.load(jsonData) #load the bibFile
        pNums = ocred.keys() #take the citation keys
        pageDic = functions.generatePageLinks(pNums) #load the function which generates links to all pages in a publication

        # load page template
        with open(settings["template_page"], "r", encoding="utf8") as ft:
            template = ft.read() #load the page template

        # load individual bib record
        bibFile = pathToBibFile #take the pathToBibFile
        bibDic = functions.loadBib(bibFile) #load the loadBib-function which loads the bibTex data into a dictionary
        bibForHTML = bibText.prettifyBib(bibDic[citeKey]["complete"]) #load the prettifyBib-function to make the bib record more readable (taking the complete bib record)

        orderedPages = list(pageDic.keys()) #create a list of keys to get all page numbers

        for o in range(0, len(orderedPages)): #loop through the pages
            #print(o)
            k = orderedPages[o] #take the number of the page as key
            v = pageDic[orderedPages[o]] #take the links to the other pages as value

            pageTemp = template #assign the page template to a temporary variable
            pageTemp = pageTemp.replace("@PAGELINKS@", v) #replace the Pagelinks item with the links to the other pages
            pageTemp = pageTemp.replace("@PATHTOFILE@", "") #replace the Pathtofile item with a blank
            pageTemp = pageTemp.replace("@CITATIONKEY@", citeKey) #replace the Citationkey item with the citation key

            emptyResults = '<tr><td><i>%s</i></td><td><i>%s</i></td><td><i>%s</i></td></tr>' #create a template for the similarity values

           if k != "DETAILS": #if the page is not the details page
                mainElement = '<img src="@PAGEFILE@" width="100%" alt="">'.replace("@PAGEFILE@", "%s.png" % k) #takes the .png-file of the OCRed text of this page

                pageKey = citeKey+"_%05d" % roundUp(int(k), 5) #take the citationKey and the pageNumbers
                #print(pageKey)
                if pageKey in pageConnData: #check if there are any similar pageclusters
                    formattedResults = "\n".join(pageConnData[pageKey]) #add them 
                    #input(formattedResults)
                else:
                    formattedResults = emptyResults % ("no data", "no data", "no data") #add that there are no similar pageclusters

                mainElement += connectionsTemplate.replace("@CONNECTEDTEXTSTEMP@", formattedResults) #replace the wildcard in the template with the actual values for simliar texts
                mainElement += ocrTemplate.replace("@OCREDCONTENTTEMP@", ocred[k].replace("\n", "<br>")) #replace the wildcard in the template with the OCRed text of the page
                pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement) #repace the wildcard with the added actual values
            else: #if the page is the details page
                reference = generateReferenceSimple(citeKey) #take the information about the publication we've generated
                mainElement = "<h3>%s</h3>\n\n" % reference #add it as a header

                bibElement = '<div class="bib">%s</div>' % bibForHTML.replace("\n", "<br> ") #take the bibliogaphical data
                bibElement = generalTemplate.replace("@ELEMENTCONTENT@", bibElement) #replace the wildcard in the general template with the bibliographical data
                bibElement = bibElement.replace("@ELEMENTHEADER@", "BibTeX Bibliographical Record") #add a meaningful description
                mainElement += bibElement + "\n\n" #add a new line

                wordCloud = '\n<img src="../' + citeKey + '_wCloud.jpg" width="100%" alt="wordcloud">' #take the wordcloud we've generated
                wordCloud = generalTemplate.replace("@ELEMENTCONTENT@", wordCloud) #replace the wildcard in the general template with the wordcloud
                wordCloud = wordCloud.replace("@ELEMENTHEADER@", "WordCloud of Keywords (<i>tf-idf</i>)") #add a meaningful description
                mainElement += wordCloud + "\n\n" #add a new line

                if citeKey in publConnData: #check if there are any similar texts
                    formattedResults = "\n".join(publConnData[citeKey]) #add them
                    #input(formattedResults)
                else:
                    formattedResults = emptyResults % ("no data", "no data", "no data") #add that there are non similar texts

                mainElement += connectionsTemplate.replace("@CONNECTEDTEXTSTEMP@", formattedResults) #replace the wildcard in the template with the actual information about similar texts


                pageTemp = pageTemp.replace("@MAINELEMENT@", mainElement) #replace the wildcard in the pagetemplate with the added content

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

            pageTemp = pageTemp.replace("@NEXTPAGEHTML@", nextPage) #replace the wildcard with a link to the page assigned in the lines before
            pageTemp = pageTemp.replace("@PREVIOUSPAGEHTML@", prevPage) #replace the Previouspagehtml item with a link to the page assigned in the lines before

            pagePath = os.path.join(pathToBibFile.replace(citeKey+".bib", ""), "pages", "%s.html" % k) #create a filepath to each page in the pages-folder of each publication
            with open(pagePath, "w", encoding="utf8") as f9:
                f9.write(pageTemp) #create and save each page in that pages folder

###########################################################
# FUNCTIONS TESTING #######################################
###########################################################

functions.memexStatusUpdates(settings["path_to_memex"], ".html") #execute the memexStatusUpdates-function
def processAllRecords(pathToMemex): 
    files = functions.dicOfRelevantFiles(pathToMemex, ".bib") #take the bibFiles
    for citeKey, pathToBibFile in files.items(): #loop through them
        if os.path.exists(pathToBibFile.replace(".bib", ".json")): #search for files with json extension
            generatePublicationInterface(citeKey, pathToBibFile) #execute the previous function

processAllRecords(settings["path_to_memex"]) #execute the overall function
exec(open("6_Interface_IndexPage.py").read())