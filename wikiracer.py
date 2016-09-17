import json
import sys
import time
import requests
from bs4 import BeautifulSoup
from collections import deque

def find_shortest_path(start, end):
    '''
    Breadth-first search approach for shortest path between two Wikipedia pages.

    path is a dict of page (key): list of links from start to page (value).
    Q is a double-ended queue of pages to visit.
    '''
    path = {}
    path[start] = [start]
    Q = deque([start])

    while len(Q) != 0:
        page = Q.popleft()
        if page == end:
            return path[page]

        links = get_links(page)

        for link in links:
            if link == end:
                return path[page] + [link]
            if (link not in path) and (link != page):
                path[link] = path[page] + [link]
                Q.append(link)
    return None

def get_links(page):
    '''
    Retrieves distinct links in a Wikipedia page.
    '''
    r = requests.get(page)
    soup = BeautifulSoup(r.content, 'html.parser')
    links = list({'https://en.wikipedia.org{}'.format(a['href']) for a in soup.select('p a[href]') if a['href'].startswith('/wiki/')})
    return links

def check_pages(start, end):
    '''
    Checks that "start" and "end "are valid Wikipedia pages of the same language.

    Valid also means that "start" is not a dead-end page (the script would return no path anyways) and that "end" is not an orphan page.
    '''
    languages = []
    for page in [start, end]:
        try:
            ind = page.find('.wikipedia.org/wiki/')
            languages.append(page[(ind-2): ind])
            requests.get(page)
        except:
            print '{} page does not appear to be a valid Wikipedia page.'.format(page.capitalize())
            return False

    if len(set(languages)) > 1:
        print 'Pages are in different languages.'
        return False

    if len(get_links(start)) == 0:
        print 'Start page is a dead-end page with no Wikipedia links.'
        return False

    end_soup = BeautifulSoup(requests.get(end).content, 'html.parser')
    if end_soup.find('table', {'class': 'metadata plainlinks ambox ambox-style ambox-Orphan'}):
        print 'End page is an orphan page with no Wikipedia pages linking to it.'
        return False

    return True

def result(path):
    '''
    Returns json object of shortest path result.
    '''
    if path:
        result = path
    else:
        result = "No path! :( "
    d = {"start": start, "end": end, "path": result}
    return json.dumps(d, indent=4)

if __name__ == '__main__':
    starttime = time.time()
    input_json = '''
    {
        "start": "https://en.wikipedia.org/wiki/Acoustic_Kitty",
        "end": "https://en.wikipedia.org/wiki/Cat"
    }
    '''
    data = json.loads(input_json)
    start = data["start"]
    end = data["end"]
    # https://en.wikipedia.org/wiki/Acoustic_Kitty
    # end='https://en.wikipedia.org/wiki/Animal_population_control'
    # start = 'https://en.wikipedia.org/wiki/Malaria'
    # end = 'https://en.wikipedia.org/wiki/Geophysics'
    # end = 'https://en.wikipedia.org/wiki/DNA_origami'
    if check_pages(start, end):
        path = find_shortest_path(start, end)
        json_result = result(path)
        print json_result
        endtime = time.time()
        totaltime = endtime - starttime
        print 'Time: {}m {:.3f}s'.format(int(totaltime)/60, totaltime%60)
