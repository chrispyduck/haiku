from abc import abstractclassmethod
import time
import yaml 

class YamlFileFormat:
  def __init__(self, id):
    self.id = id

  @abstractclassmethod
  def to_raw_object(self):
    pass

  def write(self, directory):
    obj = self.to_raw_object()
    filename = f'{directory}/{self.id}.yaml'
    with open(filename, 'w') as file:
        yaml.dump(obj, file)
        print(f'Wrote file: {filename}')

class Haiku(YamlFileFormat):
  def __init__(self, date, author, text):
    super().__init__(f'{int(time.mktime(date.timetuple()))}')
    self.date = date
    self.author = author
    self.text = text
    self.topics = []
    
  def to_raw_object(self):
    return {
      '_id': self.id,
      'timestamp': self.date.isoformat(),
      'author': self.author,
      'text': self.text,
      'topics': self.topics
    }

class Topic(YamlFileFormat):
  def __init__(self, name):
    super().__init__(name)
    self.name = name
    self.entries = []

  def to_raw_object(self):
    return {
      '_id': self.id,
      'name': self.name,
      'entries': self.entries
    }

class Author(YamlFileFormat):
  def __init__(self, name):
    super().__init__(name)
    self.name = name
    self.entries = []

  def to_raw_object(self):
    return {
      '_id': self.id,
      'name': self.name,
      'entries': self.entries
    }
