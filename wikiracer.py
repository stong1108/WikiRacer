import json
import time
import requests
import argparse
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
        # look at next page in queue of pages to visit, get wikilinks on that page
        page = Q.popleft()
        links = get_links(page)

        # look at each link on the page
        for link in links:

            # if link is our destination, we're done!
            if link in end:
                return path[page] + [link]

            # if not, check if we already have a record of the shortest path from the start page to this link- if we don't, we need to record the path and add the link to our queue of pages to explore
            if (link not in path) and (link != page):
                path[link] = path[page] + [link]
                Q.append(link)

    # if we've exhausted all possible pages to explore in our queue without getting to the destination
    return None

def get_links(page):
    '''
    Retrieves distinct links in a Wikipedia page.
    '''
    r = requests.get(page)
    soup = BeautifulSoup(r.content, 'html.parser')
    base_url = page[:page.find('/wiki/')]
    links = list({base_url + a['href'] for a in soup.select('p a[href]') if a['href'].startswith('/wiki/')})
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
            languages.append(page[(ind-2):ind])
            requests.get(page)
        except:
            print '{} does not appear to be a valid Wikipedia page.'.format(page)
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

def redirected(end):
    '''
    Returns the url that end page points to (helpful for end pages with redirected url)
    '''
    end_soup = BeautifulSoup(requests.get(end).content, 'html.parser')
    title = end_soup.find('h1').text
    title = title.replace(' ', '_', len(title))
    base_url = end[:end.find('/wiki/') + len('/wiki/')]
    return set([end, base_url + title])

def result(start, end, path):
    '''
    Returns json object of shortest path result.
    '''
    if path:
        result = path
    else:
        result = "No path! :( "
    d = {"start": start, "end": end, "path": result}
    return json.dumps(d, indent=4)

def main(args):
    '''
    Executes the WikiRacer for args (input arguments).
    '''
    input_json = args.input_json
    data = json.loads(args.input_json)
    start = data["start"]
    end = data["end"]
    if check_pages(start, end):
        path = find_shortest_path(start, redirected(end))
        json_result = result(start, end, path)
        return json_result

if __name__ == '__main__':
    starttime = time.time()

    parser = argparse.ArgumentParser(description='WikiRacer for finding the shortest path between two Wikipedia articles')
    parser.add_argument('input_json', help='JSON object with "start" & "end" name/value pairs of Wikipedia links')
    args = parser.parse_args()

    print main(args)

    endtime = time.time()
    totaltime = endtime - starttime
    print 'Time: {}m {:.3f}s'.format(int(totaltime)/60, totaltime%60)
