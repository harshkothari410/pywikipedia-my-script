#!/usr/bin/python
# -*- coding: utf-8  -*-

import re, pagegenerators, urllib2, urllib
import wikipedia as pywikibot
from pywikibot import i18n
import codecs, config
import webbrowser
import os, re, pickle, bz2
#import wikipedia as pywikibot
import catlib, config, pagegenerators
from pywikibot import i18n

docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}
'''
try:
    request = urllib2.Request(url)
    request.add_header("User-Agent", pywikibot.useragent)
    response = urllib2.urlopen(request)
    text = response.read()
    response.close()
        # When you load to many users, urllib2 can give this error.
except urllib2.HTTPError:
    pywikibot.output(u"Server error. Pausing for 10 seconds... " + time.strftime("%d %b %Y %H:%M:%S (UTC)", time.gmtime()) )
    response.close()
    time.sleep(10)
    return pageText(url)
return text
'''


'''category database'''
class CategoryDatabase:
    '''This is a temporary knowledge base saving for each category the contained
    subcategories and articles, so that category pages do not need to be loaded
    over and over again

    '''
    def __init__(self, rebuild = False, filename = 'category.dump.bz2'):
        if rebuild:
            self.rebuild()
        else:
            try:
                if not os.path.isabs(filename):
                    filename = pywikibot.config.datafilepath(filename)
                f = bz2.BZ2File(filename, 'r')
                pywikibot.output(u'Reading dump from %s'
                                 % pywikibot.config.shortpath(filename))
                databases = pickle.load(f)
                f.close()
                # keys are categories, values are 2-tuples with lists as entries.
                self.catContentDB = databases['catContentDB']
                # like the above, but for supercategories
                self.superclassDB = databases['superclassDB']
                del databases
            except:
                # If something goes wrong, just rebuild the database
                self.rebuild()

    def rebuild(self):
        self.catContentDB={}
        self.superclassDB={}

    def getSubcats(self, supercat):
        '''For a given supercategory, return a list of Categorys for all its
        subcategories. Saves this list in a temporary database so that it won't
        be loaded from the server next time it's required.

        '''
        # if we already know which subcategories exist here
        if supercat in self.catContentDB:
            return self.catContentDB[supercat][0]
        else:
            subcatlist = supercat.subcategoriesList()
            articlelist = supercat.articlesList()
            # add to dictionary
            self.catContentDB[supercat] = (subcatlist, articlelist)
            return subcatlist

    def getArticles(self, cat):
        '''For a given category, return a list of Pages for all its articles.
        Saves this list in a temporary database so that it won't be loaded from the
        server next time it's required.

        '''
        # if we already know which articles exist here
        if cat in self.catContentDB:
            return self.catContentDB[cat][1]
        else:
            subcatlist = cat.subcategoriesList()
            articlelist = cat.articlesList()
            # add to dictionary
            self.catContentDB[cat] = (subcatlist, articlelist)
            return articlelist

    def getSupercats(self, subcat):
        # if we already know which subcategories exist here
        if subcat in self.superclassDB:
            return self.superclassDB[subcat]
        else:
            supercatlist = subcat.supercategoriesList()
            # add to dictionary
            self.superclassDB[subcat] = supercatlist
            return supercatlist

    def dump(self, filename = 'category.dump.bz2'):
        '''Saves the contents of the dictionaries superclassDB and catContentDB
        to disk.

        '''
        if not os.path.isabs(filename):
            filename = pywikibot.config.datafilepath(filename)
        if self.catContentDB or self.superclassDB:
            pywikibot.output(u'Dumping to %s, please wait...'
                             % pywikibot.config.shortpath(filename))
            f = bz2.BZ2File(filename, 'w')
            databases = {
                'catContentDB': self.catContentDB,
                'superclassDB': self.superclassDB
            }
            # store dump to disk in binary format
            try:
                pickle.dump(databases, f, protocol=pickle.HIGHEST_PROTOCOL)
            except pickle.PicklingError:
                pass
            f.close()
        else:
            try:
                os.remove(filename)
            except EnvironmentError:
                pass
            else:
                pywikibot.output(u'Database is empty. %s removed'
                                 % pywikibot.config.shortpath(filename))

#fetching file
#textfile = pywikibot.input(u'Which textfile do you want to add?')
textfile = 'addtext.txt'
#fetching site
site = pywikibot.getSite()
f = codecs.open(textfile, 'r', config.textfile_encoding)
addText = f.read()
f.close()

#Bot Script written by Me in '''Python'''
#enter 1st category
cat = pywikibot.input('Enter Category name:')
#enter 2nd one
#from_cat = pywikibot.input('ENter checking category')
cat1 = catlib.Category(site, 'Category:'+ cat)
#cat2 = catlib.Category(site, 'Category:'+from_cat)
articles = cat1.articlesList(recurse = 0)
for article in articles:
	#print article
	page1 = article.title()
	print page1
	num = page1.find('(')
	print num
	if (num>0):
		#num = page1.index('(')
		pagename = page1[:num]
	else:
		pagename = page1

	pagename = unicode(pagename)
	page = pywikibot.Page(site,page1)
	#print page
	#print page.urlname()
	print pagename
	text = page.get()
	addText_temp = addText % (pagename)
	d = text.find('Infobox')
	if d>0:
		continue
	#print addText_temp
	page.put(addText_temp + text)

'''
#enter page name
page1 = pywikibot.input(u'What page do you want to use?')
#generator = [pywikibot.Page(pywikibot.getSite(), page)]
#print page1 + "  Before"

num = page1.find('(')
if (num>0):
	#num = page1.index('(')
	pagename = page1[:num]
else:
	pagename = page1

pagename = unicode(pagename)

print type(pagename)
print pagename + "  After"

addText = addText % (pagename)
print addText

page = pywikibot.Page(site,page1)
print page
#print page.urlname()
#text = page.get()
#print text

#page.put(add + text)
'''