# Building Memex

- [ 1 / #07 ] Parsing and Manipulating Bibliographic Data
	- creating the overall structure for our MEMEX on HDD
	- ./memex/data/1letter/2letters/citeKey/
		- .bib file with bibliographical info
		- .pdf file of the publication 
- [ 2 / #08 ] Processing PDFs: OCR
	- OCR every PDF in our data
		- basics of OCR with Tesseract
	- generate images of pages
	- save OCR results of every page
		- automatically pick the language
- [ 3 / #09 ] View and Display: Simple HTML-based Interface
	- we need to create a simple yet convenient interface that would allow us to read publications in memex and "cite" them
		- HTML template
		- CSS styling
- [ 4 / #10 ] Summarizing Textual Data: Keyword Extraction
	- we will need to summarize our texts: extract keywords
		- on the level of publications
		- on the level of pages
- [ 5 / #11 ] Finding Connections: Similarity Measures
	- using different similarities measures, we can compare different publications and connect them
		- create links between close publications
		- create links between close pages

- [ NB ] after this step, we should be able to open/read any publication and see links to other related publications. This should be a working version of memex. The value of it, however, will depend on its size: 10 publications will not generate interresting connections, but 1000 will.

- [ 6 / #12 ] Processing Everything Together: Batch Processing and re-Processing
- [ 7 / #13 ] Improving the Overall Memex Design: What Else Can We Add?
