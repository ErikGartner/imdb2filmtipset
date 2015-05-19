#!/usr/bin/env python

import urllib.request
import json
from random import randint
import csv
import sys
import feedparser

# program constants
program_key = 'xtyrZqwjC7I1AVrX5e0TOw'
fs_url = 'http://www.filmtipset.se/api/api.cgi'
rate_path = '%s?accesskey=%s&userkey=%s&returntype=json&action=grade&id=%s&grade=%d'
imdb_path = '%s?accesskey=%s&userkey=%s&returntype=json&action=imdb&id=%s'
imdb_ratings_rss = 'http://rss.imdb.com/user/%s/ratings'


def get_filmtipset_id(imdb_id):
    url = imdb_path % (fs_url, program_key, user_key, imdb_id)
    response = urllib.request.urlopen(url)
    data = response.read().decode('utf8','ignore')
    json_map = json.loads(data)
    movie = json_map[0]['data'][0]['movie']
    return (movie['id'], movie['name'])

def rate_filmtipset(filmtipset_id, rating):
    url = rate_path % (fs_url, program_key, user_key, filmtipset_id, rating)
    response = urllib.request.urlopen(url)
    data = response.read().decode('utf8','ignore')
    json_map = json.loads(data)
    movie = json_map[0]['data'][0]['movie']

def remove_filmtipset(filmtipset_id):
    rate_filmtipset(filmtipset_id, 0)

def translate_imdb_rating(rating):
    return translation_mapping[rating - 1]

def read_settings():
    global settings, user_key, imdb_user, translation_mapping
    try:
        with open('settings.json', 'r') as myfile:
            settings = json.load(myfile)
            user_key = settings['filmtipset_key']
            imdb_user = settings['imdb_userid']
            translation_mapping = settings['translation_mapping']
    except:
        print('Error while reading settings.json')
        sys.exit()

def get_latest_ratings(rss_url):
    feed = feedparser.parse(rss_url)
    for film in feed.entries:
        id = film.link.split('/')[-2][2:]
        rating = film.summary[:-1].split(' ')[-1]
        imdb_rating = {'title': film.title, 'id': id, 'rating': int(rating)}
        yield imdb_rating

def get_full_ratings(file):
    with open(sys.argv[1]) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            imdb_rating = {'title': row['Title'], 'id': row['const'][2:], 'rating': int(row['You rated'])}
            yield imdb_rating


read_settings()
if(len(sys.argv) == 2):
    print('Full sync from csv file')
    ratings = get_full_ratings(sys.argv[1])
    full = True
elif(len(sys.argv) == 1):
    print('Syncing latest from RSS')
    ratings = get_latest_ratings(imdb_ratings_rss % imdb_user)
    full = False
else:
    print('Invalid paramteters')
    sys.exit()

try:
    # Read cache of already transfered ratings.
    with open('cache.json', 'r') as myfile:
        cache = json.load(myfile)
except:
    cache = {}
done = {}


tries = 0
fails = 0
for rating in ratings:
    id = rating['id']
    frating = translate_imdb_rating(rating['rating'])
    if (not id in cache or frating != cache[id]['frating']):
        print('%s: %d' % (rating['title'], rating['rating']), end='')

        try:
            tries += 1
            (fid, fname) = get_filmtipset_id(id)
            rate_filmtipset(fid, frating)
            done[id] = {'irating': rating['rating'], 'frating': frating, 'err': False}
            print(' -> %d' % frating)
        except:
            done[id] = {'irating': rating['rating'], 'frating': frating, 'err': True}
            fails += 1
            print('... err!')
    else:
        done[id] = cache[id]

if full:
    done_keys = set(done.keys())
    diff = [aa for aa in cache.keys() if aa not in done_keys]
    for key in diff:
        try:
            (fid, title) = get_filmtipset_id(key)
            remove_filmtipset(fid)
            print('%s... removed!' % title)
        except:
            pass
else:
    cache.update(done)
    done = cache

print('Transfered %d ratings, %d failed.' % (tries-fails, fails))

json_string = json.dumps(done, sort_keys=True, indent=4, separators=(',', ': '))
with open('cache.json', 'w') as text_file:
    text_file.write(json_string)
