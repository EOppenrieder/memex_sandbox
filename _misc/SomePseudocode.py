import os, json
import pdf2image, pytesseract
import functions 
import yaml
import removeComments
#def generateContentPage():# 
####
#### Pseudocode: 
#### funkion: 
#### template öffnen
#### @PATHTOPUBL@, [@CITEKEY@], @AUTHOR@ (@DATE@) @TITLE@ + Link zur details(.html) des Textes
#### dictionary mit diesen variablen 
#### loop um jeweils einen citekey/text/
#### Input: citekey,Path zum file, usw. -> Output Liste###        # load page template # wir brauchen template_index.html
        #with open(settings["template_index"], "r", encoding="utf8") as ft:
         #   template = ft.read()###         
        # load individual bib record
       # bibFile = pathToBibFile
        #bibDic = functions.loadBib(bibFile)
        #bibForHTML = functions.prettifyBib(bibDic[citeKey]["complete"])####                
         #   pageTemp = template
          #  pageTemp = pageTemp.replace("@PATHTOPUBL@", v)
            #pageTemp = pageTemp.replace("@CITEKEY@", v)
           #pageTemp = pageTemp.replace("@AUTHOR@", v)
            #pageTemp = pageTemp.replace("@DATE@", v)
            #pageTemp = pageTemp.replace("@TITLE@", v)        pageDic = functions.generatePageLinks(pNums)        # load page template
        #with open(settings["template_page"], "r", encoding="utf8") as ft:
         #   template = ft.read()        # load individual bib record
        #bibFile = pathToBibFile
        #bibDic = functions.loadBib(bibFile)
        #bibForHTML = functions.prettifyBib(bibDic[citeKey]["complete"])        orderedPages = list(pageDic.keys())        for o in range(0, len(orderedPages)):
            #print(o)
         #   k = orderedPages[o]
          #  v = pageDic[orderedPages[o]]            pageTemp = template
           # pageTemp = pageTemp.replace("@PAGELINKS@", v)
            #pageTemp = pageTemp.replace("@PATHTOFILE@", "")
            #pageTemp = pageTemp.replace("@CITATIONKEY@", citeKey)