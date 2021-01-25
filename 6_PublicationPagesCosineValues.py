#function to include the cosine similarity values as tables in our memex

import functions, json, os, yaml

settingsFile = "settings.yml"
settings = yaml.safe_load(open(settingsFile))
memexPath = settings["path_to_memex"]

#take the cosine similarity values for the page clusters
# loop through our dictionary with the cosine similarity values
# take the values for each cluster of pages
# add author, year, title and number of pages
# replace the wildcards in the html-code with the actual values
# format the results in a table
#generate them for the starting page of a publication
#generate them for all the other pages of a publication
