def generatePageLinks(pNumList):
    listMod = ["DETAILS"]
    listMod.extend(pNumList)

    toc = []
    for l in listMod:
        toc.append('<a href="%s.html">%s</a>' % (l, l))
    toc = " ".join(toc)

    pageDic = {}
    for l in listMod:
        pageDic[l] = toc.replace('>%s<' % l, ' style="color: red;">%s<' % l)

    return(pageDic)
    