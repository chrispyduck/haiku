#!/usr/local/bin/python3 
 
from __future__ import print_function

import sys
import os
import yaml
import datetime
import nltk
import re

from yaml_file_types import Haiku, Topic, Author
from downloader import fetch_haiku

from stop_words import get_stop_words
from gensim import corpora, models

# The ID and range of a sample spreadsheet.


topics = {}
authors = {}
all_haiku = {}
outdir = ""
haiku_list_of_token_list = []






def check_outdir(name):
    global outdir
    local_outdir = outdir + '/' + name
    if not os.path.exists(local_outdir):
        log('Creating output directory: ' + local_outdir)
        os.makedirs(local_outdir)

def process_rows(rows):
    

def process_row(row):
    global outdir
    global authors
    global topics
    global all_haiku

    if not len(row) >= 3:
        return False
    
    # parse row and write yaml document for haiku
    
    haiku.write(outdir + '/haiku')

    process_row_author(row_id, author)
    local_topics = process_row_topics(row_id, text)

    haiku = [{
        '_id': row_id,
        'timestamp': date.isoformat(),
        'author': author,
        'text': text,
        'topics': local_topics
    }]
    all_haiku[row_id] = haiku

    return True

def process_row_topics(row_id, text):
    global topics
    global stop_words
    global haiku_list_of_token_list

    tokenized = nltk.tokenize.word_tokenize(' '.join(text))
    lemmatizer = nltk.stem.WordNetLemmatizer()

    haiku_topics = []
    for w in tokenized:
        if not re.match("^[A-Z0-9]{2,}$", w):
            w = lemmatizer.lemmatize(w).lower()
        
        if len(w) > 3 and w not in stop_words:
            haiku_topics.append(w)
            if not w in topics:
                topic = {
                    '_id': w,
                    'entries': []
                }
                topics[w] = topic
            else:
                topic = topics[w]
            topic['entries'].append(row_id)

    haiku_list_of_token_list.append(haiku_topics)
    return haiku_topics

def analyze_topics():
    global outdir
    global topics
    global haiku_list_of_token_list

    log('analyzing topics from ' + str(len(haiku_list_of_token_list)) + ' haiku')
    dictionary_LDA = corpora.Dictionary(haiku_list_of_token_list)
    dictionary_LDA.filter_extremes(no_below=4)
    corpus = [
        dictionary_LDA.doc2bow(list_of_tokens) 
        for list_of_tokens in haiku_list_of_token_list
    ]
    log('created dict with size: ' + str(len(dictionary_LDA)))
    log('created corpus with size: ' + str(len(corpus)))

    num_topics = 6
    lda_model = models.LdaModel(corpus, num_topics=num_topics, \
                                    id2word=dictionary_LDA, \
                                    passes=4, alpha=[0.01]*num_topics, \
                                    eta=[0.01]*len(dictionary_LDA.keys()))
    for i,topic in lda_model.show_topics(formatted=True, num_topics=num_topics, num_words=10):
        print(str(i)+": "+ topic)
        print()



def write_topics():
    sorted_topics = sorted(topics.items(), key=lambda item: len(item[1]['entries']), reverse=True)
    for topic_tuple in sorted_topics:
        topic = topic_tuple[1]
        if len(topic['entries']) > 2:
            key = topic['_id']
            with open(outdir + '/topics/' + key + r'.yaml', 'w') as file:
                yaml.dump(topic, file)
            log('Wrote topic: ' + key + '.yaml')



def main():
    global outdir 

    check_dependencies()

    log('Connecting to sheets API...')


    if len(sys.argv) != 2:
        log('ERROR: usage: ' + sys.argv[0] + ' <output directory>')
        return 1
    outdir = sys.argv[1]
    if not outdir:
        log('ERROR: usage: ' + sys.argv[0] + ' <output directory>')
        return 1
    
    check_outdir("haiku")
    check_outdir("authors")
    check_outdir("topics")
    
    haiku = fetch_haiku(api_key)
    write_authors()
    write_topics()
        
if __name__ == '__main__':
    main()