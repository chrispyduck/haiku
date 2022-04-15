#!/usr/local/bin/python3

import logging
from sys import stderr, argv
from os import environ, makedirs, path
from downloader import fetch_haiku
from yaml_file_types import Haiku, Author, Topic


class SiteDataGenerator:
    def __init__(self, output_directory):
        self.haiku = []
        self.topics = {}
        self.authors = {}
        self.output_directory = output_directory

    def make_outdir(self, name):
        local_outdir = self.output_directory + '/' + name
        if not path.exists(local_outdir):
            logging.info('Creating output directory: ' + local_outdir)
            makedirs(local_outdir)
        return local_outdir

    def load_haiku(self, api_key):
        self.haiku = fetch_haiku(api_key)

    def process_authors(self):
        for haiku in self.haiku:
            if haiku.author not in self.authors:
                author = self.authors[haiku.author] = Author(haiku.author)
            else:
                author = self.authors[haiku.author]

            author.entries.append(haiku.id)

    def process_topics(self):
        for haiku in self.haiku:
            for topic_name in haiku.topics:
                if topic_name not in self.topics:
                    topic = self.topics[topic_name] = Topic(topic_name)
                else:
                    topic = self.topics[topic_name]

                topic.entries.append(haiku.id)

    def write_files(self):
        [haiku.write(self.make_outdir('haiku')) for haiku in self.haiku]
        [author.write(self.make_outdir('authors')) for author in self.authors.values()]
        [topic.write(self.make_outdir('topics')) for topic in self.topics.values()]


if __name__ == '__main__':
    logging.basicConfig(
        stream=stderr,
        level=logging.DEBUG,
        format='%(asctime)s : %(levelname)s : %(message)s')

    api_key = environ.get('GCP_API_KEY')
    if not api_key:
        logging.error('ERROR: no GCP_API_KEY environment variable specified')
        exit(2)

    if len(argv) != 2:
        logging.error(f'ERROR: usage: {argv[0]} <output directory>')
        exit(1)
    outdir = argv[1]
    if not outdir:
        logging.error(f'ERROR: usage: {argv[0]} <output directory>')
        exit(1)

    generator = SiteDataGenerator(outdir)
    generator.load_haiku(api_key)
    generator.process_authors()
    generator.process_topics()
    generator.write_files()
