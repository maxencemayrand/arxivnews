from sys import argv
import feedparser
import os

def clearscreen():
    """
    Cross-platform method to clear the terminal.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def boxed(title):
    """
    Display 'title' in a box.
    """
    print('*' + '-' * (4 + len(title)) + '*' + '   enter: next paper     nc: next category')
    print("|  " + title + "  |" + '   p: previous paper     pc: previous category')
    print('*' + '-' * (4 + len(title)) + '*' + '   q: quit')

class Paper:
    """
    Metadata of an arxiv paper.
    """
    def __init__(self):
        self.title = None       # string
        self.authors = None     # list of strings
        self.abstract = None    # string
        self.published = None   # time.struct_time
        self.updated = None     # time.struct_time
        self.date = None        # tuple, e.g. (2018, 3, 24)
        self.tags = None        # list of strings, e.g. ('math.DG', 'math.AG')
        self.new = None         # boole
        self.id = None          # string (url)
        self.flags = []         # list of strings

    def init_from_feed(self, p, flags_list):
        """
        Initialize from an element `p` of `f.entries` where
        `f = feedparser.parse(url)` for some url.

        Examples of url:
            http://export.arxiv.org/rss/math.AG
            http://export.arxiv.org/api/query?id_list=1803.10893,1803.10894&max_results=2
        """
        self.title = p.title
        self.authors = [a.name for a in p.authors]
        self.abstract = p.summary
        self.tags = [t.term for t in p.tags]
        self.id = p.id

        self.published = p.published_parsed
        self.updated = p.updated_parsed
        if self.published == self.updated:
            self.new = True
        else:
            self.new = False

        self.date = (self.published.tm_year, self.published.tm_mon,
                        self.published.tm_mday)

        for f in flags_list:
            if f.lower() in (self.title + self.abstract +
                                ''.join(self.authors)).lower():
                self.flags.append(f)

    def display(self):
        """
        Display the info of the paper on the terminal.
        """
        print()
        if len(self.flags) > 0:
            for f in self.flags:
                print("   * " + f)
            print()
        print(self.title)
        print("\t" + ", ".join(self.authors))
        print("\t%4d-%02d-%02d" % self.date, end=' ')
        if self.new:
            print("NEW")
        else:
            print("REVISED")
        print("\t" + " ".join(self.tags))
        print('\t' + self.id)
        print(self.abstract)
        print()

class Category:
    """
    List of `Paper` objects in the same category.
    """
    def __init__(self, papers=None, name=None):
        self.papers = papers    # list of `Paper` objects
        self.name = name        # the name of the category, e.g 'math.DG'
        self.size = len(self.papers) if self.papers != None else None

def read_categories_names(subscriptions):
    """
    Return a list of the categories in the file `subscriptions`.
    Example of output:
        ['math.DG', 'math.AG']
    """
    categories_names = []
    with open(subscriptions, 'r') as f:
        for cat in f:
            categories_names.append(cat.strip())
    return categories_names

def read_flags(flags):
    """
    Return a list of the flags in the file `flags`.
    Example of output:
        ['hyperkahler', 'stratification']
    """
    flags_list = []
    with open(flags, 'r') as f:
        for cat in f:
            flags_list.append(cat.strip())
    return flags_list

def get_id_list(cat):
    """
    Use arxiv's rss to obtain a list of the ids of the new articles
    in the category 'cat'.
    Example of output:
        ['1803.08734', '1803.08735', '1803.08750', '1803.08871']
    """
    url = 'http://export.arxiv.org/rss/' + cat
    f = feedparser.parse(url)
    ids = []
    for p in f.entries:
        link = p.link
        ids.append(link[21:])
    return ids

def get_categories(subscriptions, flags):
    """
    Return a list of `Category` objects.
    """
    categories_names = read_categories_names(subscriptions)
    flags_list = read_flags(flags)
    categories = []
    for cat_name in categories_names:
        print('Loading ' + cat_name + ':', end=' ')
        ids = get_id_list(cat_name)
        print("%d papers." % len(ids))
        url = 'http://export.arxiv.org/api/query?id_list='
        url += ",".join(ids)
        url += "&max_results={0}".format(len(ids))
        f = feedparser.parse(url)
        papers = []
        for p in f.entries:
            if p.title != "Error":
                paper = Paper()
                paper.init_from_feed(p, flags_list)
                papers.append(paper)
        papers.sort(key=lambda p: p.published, reverse=True)
        lop = Category(papers, cat_name)
        categories.append(lop)
    return categories

def news(subscriptions, flags):
    """
    Display on the terminal the new articles in each of the
    categories contained in the file `subscriptions`.
    """
    categories = get_categories(subscriptions, flags)
    input("\nPress enter to continue. ")
    i = 0
    while i < len(categories):
        c = categories[i]
        j = 0
        while j < c.size:
            clearscreen()
            title = c.name
            title += "  {:2d}/{:2d}".format(j + 1, c.size)
            boxed(title)
            c.papers[j].display()
            inp = input()
            if inp == 'p':
                j -= 1
                if j < 0:
                    i -= 1
                    if i < 0:
                        i = 0
                        j = 0
                    else:
                        c = categories[i]
                        j = len(c.papers) - 1
            elif inp == 'nc' or inp == 'pc' or inp == 'q':
                break
            else:
                j += 1
        if inp == 'pc':
            i -= 1
            if i < 0:
                i = 0
        elif inp == 'q':
            break
        else:
            i += 1

if __name__ == '__main__':
    news(argv[1], argv[2])
    clearscreen()
