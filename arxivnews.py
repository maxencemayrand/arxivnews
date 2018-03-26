from sys import argv
import feedparser
import os

def clearscreen():
    """
    Cross-platform method to clear the terminal
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def boxed(title):
    """
    Display 'title' in a box
    """
    print('*' + '-' * (6 + len(title)) + '*')
    print("|   " + title + "   |")
    print('*' + '-' * (6 + len(title)) + '*')

def get_categories():
    """
    Return a list of the categories in the file 'subscriptions.csv'
    Example of output: ['math.DG', 'math.AG']
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
        print('Loading...')
        ids = get_id_list(cat)
        url = 'http://export.arxiv.org/api/query?id_list='
        url += ",".join(ids)
        url += "&max_results={0}".format(len(ids))
        f = feedparser.parse(url)
        for p in f.entries:
            # Each 'p' contains the information of an article in the
            # category 'cat'
            clearscreen()
            boxed(cat)
            date = p.published_parsed
            if date == p.updated_parsed:
                print("\nNEW\n")
            else:
                print("\nREVISED\n")
            print(p.title)
            authors = [a.name for a in p.authors]
            print("\t" + ", ".join(authors))
            print("\t%4d-%02d-%02d" % (date.tm_year, date.tm_mon, date.tm_mday))
            print("\t" + " ".join([t.term for t in p.tags]))
            print('\t' + p.id)
            print(p.summary)
            input() # Wait for the user to press enter

news()
