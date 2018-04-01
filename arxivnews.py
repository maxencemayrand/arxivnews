from sys import argv
import feedparser
import os

class Paper:
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

    def init_from_feed(self, p):
        """
        Initialize from an element `p` of `f.entries` where
        `f = feedparser.parse(url)` for some url.
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

    def display(self):
        """
        Display the info of the paper on the terminal.
        """
        if self.new:
            print("\nNEW\n")
        else:
            print("\nREVISED\n")
        print(self.title)
        print("\t" + ", ".join(self.authors))
        print("\t%4d-%02d-%02d" % self.date)
        print("\t" + " ".join(self.tags))
        print('\t' + self.id)
        print(self.abstract)

def clearscreen():
    """
    Cross-platform method to clear the terminal.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def boxed(title):
    """
    Display 'title' in a box.
    """
    print('*' + '-' * (6 + len(title)) + '*')
    print("|   " + title + "   |")
    print('*' + '-' * (6 + len(title)) + '*')

def get_categories():
    """
    Return a list of the categories in the file 'subscriptions.csv'
    Example of output:
        ['math.DG', 'math.AG']
    """
    categories = []
    with open(argv[1], 'r') as f:
        for cat in f:
            categories.append(cat.strip().rstrip(','))
    return categories

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
        i = link.rfind('/')
        ids.append(link[i + 1:])
    return ids

def news():
    """
    Display on the terminal the new articles in each of the
    categories contained in the file 'subscriptions.csv'.
    """
    categories = get_categories()
    for cat in categories:
        clearscreen()
        print('Loading ' + cat + '...')
        ids = get_id_list(cat)
        url = 'http://export.arxiv.org/api/query?id_list='
        url += ",".join(ids)
        url += "&max_results={0}".format(len(ids))
        f = feedparser.parse(url)
        papers = []
        for p in f.entries:
            paper = Paper()
            paper.init_from_feed(p)
            papers.append(paper)
        papers.sort(key=lambda p: p.published, reverse=True)
        for paper in papers:
            clearscreen()
            boxed(cat)
            paper.display()
            input() # Wait for the user to press enter


news()
