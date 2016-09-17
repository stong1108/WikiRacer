import json
import sys
import time
import requests
from bs4 import BeautifulSoup
from collections import deque

def find_shortest_path(start, end):
    path = {}
    path[start] = [start]
    Q = deque([start])

    while len(Q) != 0:
        # print len(Q)
        page = Q.popleft()
        if page == end:
            return path[page]

        r = requests.get(page)
        soup = BeautifulSoup(r.content, 'html.parser')
        neighbors = list({'https://en.wikipedia.org{}'.format(a['href']) for a in soup.select('p a[href]') if a['href'].startswith('/wiki/')})

        for neighbor in neighbors:
            if neighbor == end:
                return path[page] + [neighbor]
            if (neighbor not in path) and (neighbor != page):
                path[neighbor] = path[page] + [neighbor]
                Q.append(neighbor)
    return None

def check_page(page):
    try:
        requests.get(page)
    except:
        return False
    return True

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
        "start": "https://en.wikipedia.org/wiki/Malaria",
        "end": "https://en.wikipedia.org/wiki/DNA_replication"
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
    if check_page(start) and check_page(end):
        path = find_shortest_path(start, end)
        json_result = result(path)
        print json_result
        endtime = time.time()
        print endtime-starttime
    else:
        print 'Check your start & end links'
