import os, json, yaml #import several libraries we need
import unicodedata

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions #import our script with the previous functions

###########################################################
# VARIABLES ###############################################
###########################################################

settingsFile = "settings.yml" #define our settings file
settings = yaml.safe_load(open(settingsFile)) #load our settings file
memexPath = settings["path_to_memex"] #define the memexPath
###########################################################
# MINI TEMPLATES ##########################################
###########################################################

generalTemplate = """
<button class="collapsible">@ELEMENTHEADER@</button>
<div class="content">

@ELEMENTCONTENT@

</div>
"""
#define the generalTemplate 
searchesTemplate = """
<button class="collapsible">SAVED SEARCHES</button>
<div class="content">
<table id="" class="display" width="100%">
<thead>
    <tr>
        <th><i>link</i></th>
        <th>search string</th>
        <th># of publications with matches</th>
        <th>time stamp</th>
    </tr>
</thead>

<tbody>
@TABLECONTENTS@
</tbody>

</table>
</div>
"""
#define the searchesTemplate for the searches on our index page

publicationsTemplate = """
<button class="collapsible">PUBLICATIONS INCLUDED INTO MEMEX</button>
<div class="content">
<table id="" class="display" width="100%">
<thead>
    <tr>
        <th><i>link</i></th>
        <th>citeKey, author, date, title</th>
    </tr>
</thead>

<tbody>
@TABLECONTENTS@
</tbody>

</table>
</div>
"""
#define the publicationsTemplate for the publications on our index page

###########################################################
# MINI FUNCTIONS ##########################################
###########################################################

# generate search pages and TOC
def formatSearches(pathToMemex): #define a function for the formatting of the searches
    with open(settings["template_search"], "r", encoding="utf8") as f1:
        indexTmpl = f1.read() #open the searchTemplate
    dof = functions.dicOfRelevantFiles(pathToMemex, ".searchResults") #choose the files with the search results
    # format individual search pages
    toc = [] #create an empty list
    for file, pathToFile in dof.items(): #loop through the files with the searches
        searchResults = [] #create an empty list
        data = json.load(open(pathToFile, "r", encoding="utf8")) #load the files with the search results
        # collect toc
        template = "<tr> <td>%s</td> <td>%s</td> <td>%s</td> <td>%s</td></tr>" #create the format of the table

        # variables
        linkToSearch = os.path.join("searches", file+".html") #define the link to the html-file with our search results
        pathToPage = '<a href="%s"><i>read</i></a>' % linkToSearch #create the link in the table to the html-file with our search results
        searchString = '<div class="searchString">%s</div>' % data.pop("searchString") #take the searchstring from the files with our search results 
        timeStamp = data.pop("timestamp") #take the timestamp
        tocItem = template % (pathToPage, searchString, len(data), timeStamp) #add the variables to the template
        toc.append(tocItem) #add the template to the table of contents

        # generate the results page
        keys = sorted(data.keys(), reverse=True) #sort the citation keys with the number of pages with results in reverse order
        for k in keys: #loop through each citation key
            searchResSingle = [] #create an empty list
            results = data[k] #take the citation keys and the number of pages with results
            temp = k.split("::::") #split the citation keys and the number of pages with results
            header = "%s (pages with results: %d)" % (temp[1], int(temp[0])) #create a header for each publication with citation key and the number of pages with results
            #print(header)
            for page, excerpt in results.items(): #loop through the results
                #print(excerpt["result"])
                pdfPage = int(page) #take the page with the searchstring
                linkToPage = '<a href="../%s"><i>go to the original page...</i></a>' % excerpt["pathToPage"] #add a link to the original page with the search result
                searchResSingle.append("<li><b><hr>(pdfPage: %d)</b><hr> %s <hr> %s </li>" % (pdfPage, excerpt["result"], linkToPage)) #add the text and the link to the list
            searchResSingle = "<ul>\n%s\n</ul>" % "\n".join(searchResSingle) #jpin the single pages together
            searchResSingle = generalTemplate.replace("@ELEMENTHEADER@", header).replace("@ELEMENTCONTENT@", searchResSingle) #replace the wildcards in the template
            searchResults.append(searchResSingle) #append the results
        
        searchResults = "<h2>SEARCH RESULTS FOR: <i>%s</i></h2>\n\n" % searchString + "\n\n".join(searchResults) #create a header for the html-page and join the search results
        with open(pathToFile.replace(".searchResults", ".html"), "w", encoding="utf8") as f9:
            f9.write(indexTmpl.replace("@MAINCONTENT@", searchResults)) #create the html-page
        #os.remove(pathToFile)
        
    #input("\n".join(toc))
    toc = searchesTemplate.replace("@TABLECONTENTS@", "\n".join(toc)) #replace the wildcard in the table of contents
    return(toc)


def formatPublList(pathToMemex): #define a function for the formatting of the publications
    ocrFiles = functions.dicOfRelevantFiles(pathToMemex, settings["ocr_results"]) #take the files with the OCRed pages
    bibFiles = functions.dicOfRelevantFiles(pathToMemex, ".bib") #take the bibFiles

    contentsList = [] #create an empty list

    for key, value in ocrFiles.items(): #loop through the OCRed pages
        if key in bibFiles: #search for the key in the bibFile
            bibRecord = functions.loadBib(bibFiles[key]) #load the bibliographical data for this item
            bibRecord = bibRecord[key] #take the key

            relativePath = functions.generatePublPath(pathToMemex, key).replace(pathToMemex, "") #take the relative path to the publication

            authorOrEditor = "[No data]" #take no information on the author as default setting
            if "editor" in bibRecord: #check if there is information about the editor
                authorOrEditor = bibRecord["editor"] #insert it
            if "author" in bibRecord: #check if there is information about the author
                authorOrEditor = bibRecord["author"] #insert it

            date = bibRecord["year"][:4] #insert the year of the publication
            title = bibRecord["title"] #insert the title

            # formatting template
            citeKey = '<div class="ID">[%s]</div>' % key #take the citeKey
            publication = '%s (%s) <i>%s</i>' % (authorOrEditor, date, title) #take the information about the publication and format it
            search = unicodedata.normalize('NFKD', publication).encode('ascii','ignore') #replace diacritical characters with their ascii equivalents
            publication += " <div class='hidden'>%s</div>" % search #repeat the information and hide it
            link = '<a href="%s/pages/DETAILS.html"><i>read</i></a>' % relativePath #add the link to the details page of each publication

            singleItemTemplate = '<tr><td>%s</td><td>%s %s</td></tr>' % (link, citeKey, publication) #collect the information in a single template
            recordToAdd = singleItemTemplate.replace("{", "").replace("}", "") #remove curly brackets

            contentsList.append(recordToAdd) #add the single records to the content list

    contents = "\n".join(sorted(contentsList)) #join the sorted content list
    final = publicationsTemplate.replace("@TABLECONTENTS@", contents) #replace the wildcard in the template with the actual content
    return(final) #return this variable

###########################################################
# MAIN FUNCTIONS ##########################################
###########################################################

# generate index pages: index with stats; search results pages
def generateIngexInterface(pathToMemex):
    print("\tgenerating main index page...")
    # generate the main index page with stats
    with open(settings["template_index"], "r", encoding="utf8") as f1:
        indexTmpl = f1.read() #open the index page template
    with open(settings["content_index"], "r", encoding="utf8") as f1:
        indexCont = f1.read() #open the index content page

    # - PREAMBLE
    mainElement   = indexCont + "\n\n" #add the index content
    # - SEARCHES
    mainElement += formatSearches(pathToMemex) #add the searches table
    # - PUBLICATION LIST
    mainElement += formatPublList(pathToMemex) #add the publication table

    # - FINALIZING INDEX PAGE
    indexPage     = indexTmpl #take the index page template
    indexPage     = indexPage.replace("@MAINCONTENT@", mainElement) #replace the wildcard in the template with the actual content

    pathToIndex   = os.path.join(pathToMemex, "index.html") #take the html-page as a file
    with open(pathToIndex, "w", encoding="utf8") as f9:
        f9.write(indexPage) #create an html-file and save it in our memex-sandbox folder

###########################################################
# FUNCTIONS TESTING #######################################
###########################################################

generateIngexInterface(settings["path_to_memex"]) #execute the function