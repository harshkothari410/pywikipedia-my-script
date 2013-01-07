import os, re, pickle, bz2
import wikipedia as pywikibot
import catlib, config, pagegenerators
from pywikibot import i18n

docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}

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


class CategoryRemoveRobot:
    '''Removes the category tag from all pages in a given category
    and from the category pages of all subcategories, without prompting.
    Does not remove category tags pointing at subcategories.

    '''

    def __init__(self, catTitle, cat_del,batchMode = False, editSummary = '', useSummaryForDeletion = True, titleRegex = None, inPlace = False):
        self.editSummary = editSummary
        self.site = pywikibot.getSite()
        self.cat = catlib.Category(self.site, 'Category:'+ catTitle)
        self.cat_del = catlib.Category(self.site, 'Category:'+ cat_del)
        # get edit summary message
        self.useSummaryForDeletion = useSummaryForDeletion
        self.batchMode = batchMode
        self.titleRegex = titleRegex
        self.inPlace = inPlace
        
        if not self.editSummary:
            self.editSummary = i18n.twtranslate(self.site, 'category-removing',
                                                {'oldcat': self.cat.title()})

    #rem_cat = raw_input("Enter the category name for deletion")
    #rem_cat1 = catlib.Category(self.site, 'Category:'+ rem_cat)
    def run(self):
        #print catTitle + cat_del
        articles = self.cat.articlesList(recurse = 0)
        if len(articles) == 0:
            pywikibot.output(u'There are no articles in category %s' % self.cat.title())
        else:
            for article in articles:
                if not self.titleRegex or re.search(self.titleRegex,article.title()):
                    catlib.change_category(article, self.cat_del, None, comment = self.editSummary, inPlace = self.inPlace)
        # Also removes the category tag from subcategories' pages
        subcategories = self.cat.subcategoriesList(recurse = 0)
        if len(subcategories) == 0:
            pywikibot.output(u'There are no subcategories in category %s' % self.cat.title())
        else:
            for subcategory in subcategories:
                catlib.change_category(subcategory, self.cat, None, comment = self.editSummary, inPlace = self.inPlace)
        # Deletes the category page
        if self.cat_del.exists() and self.cat_del.isEmptyCategory():
            if self.useSummaryForDeletion and self.editSummary:
                reason = self.editSummary
            else:
                reason = i18n.twtranslate(self.site, 'category-was-disbanded')
            talkPage = self.cat_del.toggleTalkPage()
            try:
                self.cat_del.delete(reason, not self.batchMode)
            except pywikibot.NoUsername:
                pywikibot.output(u'You\'re not setup sysop info, category will not delete.' % self.cat_del.site())
                return
            if (talkPage.exists()):
                talkPage.delete(reason=reason, prompt=not self.batchMode)



def main():
    global catDB

    fromGiven = False
    toGiven = False
    batchMode = False
    editSummary = ''
    inPlace = False
    overwrite = False
    showImages = False
    talkPages = False
    recurse = False
    withHistory = False
    titleRegex = None

    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages
    # to work on.
    genFactory = pagegenerators.GeneratorFactory()
    # The generator gives the pages that should be worked upon.
    gen = None

    # If this is set to true then the custom edit summary given for removing
    # categories from articles will also be used as the deletion reason.
    useSummaryForDeletion = True
    catDB = CategoryDatabase()
    action = None
    sort_by_last_name = False
    restore = False
    create_pages = False
    
   
    if (fromGiven == False):
        oldCatTitle = pywikibot.input('Enter the category from which you want to delete another category :')

    cat_name = pywikibot.input('Enter the name of category which you want to delete :')
    print cat_name + oldCatTitle
    bot = CategoryRemoveRobot(oldCatTitle, cat_name, batchMode, editSummary,
                                  useSummaryForDeletion, inPlace=inPlace)
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        catDB.dump()
        pywikibot.stopme()
