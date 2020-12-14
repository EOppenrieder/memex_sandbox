# generate interface for the publication
import json
import functions
import yaml
import os
import generate
import bibText
import dic

settingsFile = "./settings.yml"
settings = yaml.load(open(settingsFile), Loader = yaml.FullLoader)

memexPath = settings["path_to_memex"]

def generateContentPage(citeKey, pathToBibFile):

    print("="*80)
    print(citeKey)
    print(pathToBibFile)

    # load page template
    with open(settings["template_index"], "r", encoding="utf8") as ft:
            template = ft.read()
    
    # load individual bib record
    bibFile = pathToBibFile
    bibDic = functions.loadBib(bibFile)
    bibForHTML = bibText.prettifyBib(bibDic[citeKey]["complete"])

    pageTemp = template
    #insert <h1>CONTENTS OF MEMEX</h1>
    #pageTemp = template_index.replace("@MAINCONTENT@", "<li><a href="@PATHTOPUBL@/pages/DETAILS.html">[@CITEKEY@]</a> @AUTHOR@ (@DATE@) - <i>@TITLE@</i></li>")
    #create a list with all records that contains the path, the author, the date, the title and the citationKey of each publication
    #loop through all the publications
    #for every publication, replace "@PATHTOPUBL", "@AUTHOR" etc. with the actual value
    # output the actual values for each publication
    #add each output to the previous one
    #write the content.html page
    #with open(pageContent, "w", encoding="utf8") as f9:
    #    f9.write(pageTemp)

