import json
import time
import requests
import threading
from multiprocessing.pool import ThreadPool
from multiprocessing import Manager
from bs4 import BeautifulSoup
from collections import deque

def check_page(page):
    try:
        requests.get(page)
    except:
        return False
    return True

def thread_do_all(Q, path, page, link):
    r = requests.get(page)
    soup = BeautifulSoup(r.content, 'html.parser')
    links = list({'https://en.wikipedia.org{}'.format(a['href']) for a in soup.select('p a[href]') if a['href'].startswith('/wiki/')})

    if (neighbor not in path) and (neighbor != page):
        path[neighbor] = path[page] + [neighbor]
        Q.append(neighbor)
    return Q

def thread_populate(path, page, link, end):
    if link == end:
        return path[page] + [link]
    if (link not in path) and (link != page):
        path[link] = path[page] + [link]
        return link

def get_links(page):
    r = requests.get(page)
    soup = BeautifulSoup(r.content, 'html.parser')
    links = list({'https://en.wikipedia.org{}'.format(a['href']) for a in soup.select('p a[href]') if a['href'].startswith('/wiki/')})
    return links

def find_shortest_path(start, end):
    path = Manager().dict()
    path[start] = [start]
    Q = deque([start])

    while len(Q) != 0:
        page = Q.popleft()

        links = get_links(page)
        pool = ThreadPool(processes=len(links))
        results = [pool.apply(thread_populate, args=(path, page, link, end)) for link in links]
        pool.terminate()
        for result in results:
            if type(result) == list:
                return result
            Q.append(result)

    return None

def result(path):
    if path:
        result = path
    else:
        result = "No path! :( "
    d = {"start": start, "end": end, "path": path}
    return json.dumps(d, indent=4)

if __name__ == '__main__':
    starttime = time.time()
    input_json = '''
    {
        "start": "https://en.wikipedia.org/wiki/Acoustic_Kitty",
        "end": "https://en.wikipedia.org/wiki/Animal_population_control"
    }
    '''
    data = json.loads(input_json)
    start = data["start"]
    end = data["end"]
    # https://en.wikipedia.org/wiki/Acoustic_Kitty
    # https://en.wikipedia.org/wiki/Cat
    # end='https://en.wikipedia.org/wiki/Animal_population_control'
    # start = 'https://en.wikipedia.org/wiki/Malaria'
    # end = 'https://en.wikipedia.org/wiki/Geophysics'
    # end = 'https://en.wikipedia.org/wiki/DNA_origami'
    if check_page(start) and check_page(end):
        path = find_shortest_path(start, end)
        json_result = result(path)
        print json_result
        endtime = time.time()
        print endtime-starttime
    else:
        print 'Check your start & end links'
