import re, os, yaml, json, random #import various libraries
from datetime import datetime #import the timestamp extension from the datetime library

# SCRIPT WITH OUR PREVIOUS FUNCTIONS
import functions #import the script with our previous functions

###########################################################
# VARIABLES ###############################################
###########################################################

settings = functions.loadYmlSettings("settings.yml") #load our settings file

###########################################################
# FUNCTIONS ###############################################
###########################################################

def searchOCRresults(pathToMemex, searchString): #define a function that searches through our OCRed results
    print("SEARCHING FOR: `%s`" % searchString) #print a statement to keep us updated what is happening
    files = functions.dicOfRelevantFiles(pathToMemex, ".json") #generate a dictionary with citekeys as keys and paths to json-Files as values
    results = {} #create an empty dictionary

    for citationKey, pathToJSON in files.items(): #loop through all our files
        data = json.load(open(pathToJSON)) #load each OCRed publication
        #print(citationKey)
        count = 0 #count the matches in each publication

        for pageNumber, pageText in data.items(): #loop through each page in the publication
            if re.search(r"\b%s\b" % searchString, pageText, flags=re.IGNORECASE): #check if our searchphrase is matched on the page, ignore capital letters
                if citationKey not in results: #check if the citationKey is already in the results, if not:
                    results[citationKey] = {} #assign the citationKey as key to our dictionary

                # relative path
                a = citationKey.lower() #create a variable for the citationKey, using only lowercase letters
                relPath = os.path.join(a[:1], a[:2], citationKey, "pages", "%s.html" % pageNumber) #assign the relative path to the html-page where the searchphrase is matched
                countM = len(re.findall(r"\b%s\b" % searchString, pageText, flags=re.IGNORECASE)) #count the matches for the searchphrase on the page
                pageWithHighlights = re.sub(r"\b(%s)\b" % searchString, r"<span class='searchResult'>\1</span>", pageText, flags=re.IGNORECASE) #highlight the match on the page

                results[citationKey][pageNumber] = {} #create a subdictionary with the pageNumber as key
                results[citationKey][pageNumber]["pathToPage"] = relPath #add the relative path to the html-page into this subdictionary
                results[citationKey][pageNumber]["matches"] = countM #add the number of matches into this subdictionary
                results[citationKey][pageNumber]["result"] = pageWithHighlights.replace("\n", "<br>") #add the formatted page with the highlighted match(es)

                count  += 1 #increase the number of matches in each publication 

        if count > 0: #if there is at least one match in the publication
            print("\t", citationKey, " : ", count) #print the citationKey of the publication and the number of matches in the publication
            newKey = "%09d::::%s" % (count, citationKey) #create a  new key for each publication, which combines the number of matches and the citationKey
            results[newKey] = results.pop(citationKey) #replace the citationKey in the dictionary with the new key

            # add time stamp
            currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #save the current timestamp
            results["timestamp"] = currentTime #add the timestamp to the dictionary
            # add search string (as submitted)
            results["searchString"] = searchString #add the searchphrase to the dictionary

    saveWith = re.sub("\W+", "", searchString) #remove nonletter characters and add the searchphrase
    saveTo = os.path.join(pathToMemex, "searches", "%s.searchResults" % saveWith) #create a filepath and a filename
    with open(saveTo, 'w', encoding='utf8') as f9c:
        json.dump(results, f9c, sort_keys=True, indent=4, ensure_ascii=False) #create a file that saves the dictionary with the results of our search and save it

###########################################################
# RUN THE MAIN CODE #######################################
###########################################################

searchPhrase  = r"corpus\W*based" #insert a searchphrase in the form of a regular expression
#searchPhrase  = r"corpus\W*driven"
#searchPhrase  = r"multi\W*verse"
#searchPhrase  = r"text does ?n[o\W]t exist"
#searchPhrase  = r"corpus-?based"

searchOCRresults(settings["path_to_memex"], searchPhrase) #execute the function
#exec(open("9_Interface_IndexPage.py").read())