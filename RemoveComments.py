import os
import yaml
import PyPDF2
import functions

settingsFile = "./settings.yml"
settings = yaml.load(open(settingsFile), Loader = yaml.FullLoader)

memexPath = settings["path_to_memex"]
citationKey = "baumgart_wiener_2015"
publPath = functions.generatePublPath(memexPath, citationKey) 
#publPath = publPath.replace ("\\:", "\:")

pathToPdf = publPath + "\\" + citationKey + ".pdf"

def removeCommentsFromPDF(pathToPdf):
    with open(pathToPdf, 'rb') as pdf_obj:
        pdf = PyPDF2.PdfFileReader(pdf_obj)
        out = PyPDF2.PdfFileWriter()
        for page in pdf.pages:
            out.addPage(page)
            out.removeLinks()
        tempPDF = pathToPdf.replace(".pdf", "_TEMP.pdf")
        with open(tempPDF, 'wb') as f: 
            out.write(f)
    return(tempPDF)

removeCommentsFromPDF(pathToPdf)

print("done")