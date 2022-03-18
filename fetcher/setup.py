from setuptools import setup

setup(name='haiku-fetcher',
      version='0.1',
      description='It gets the Haiku and puts it on it\'s website',
      license='MIT',
      packages=[''],
      install_requires=[
          'google-api-python-client',
          'google-auth-httplib2',
          'google-auth-oauthlib',
          'pyyaml'
      ])