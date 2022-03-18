# syntax=docker/dockerfile-upstream:1.3.1-labs

ARG GCP_API_KEY
ARG GH_TOKEN

FROM docker.io/google/cloud-sdk:377.0.0-slim AS fetcher

WORKDIR /work
RUN mkdir -p /work/jekyll/_data/haiku/

# install fetcher dependencies 
RUN pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib pyyaml

# fetch data
ADD fetcher/fetch-haiku.py /work/fetcher/
ARG GCP_API_KEY
RUN python3 fetcher/fetch-haiku.py /work/out

FROM docker.io/ruby:3 AS jekyll-build
RUN gem install bundler
WORKDIR /work

# install jekyll dependencies 
COPY jekyll/Gemfile* /work/
RUN bundle install

# build page
COPY jekyll /work
COPY --from=fetcher /work/out/ /work/_data/haiku/
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" /tmp/skipcache
RUN jekyll build 

FROM docker.io/alpine/git:v2.32.0 AS publish
# configure git client
RUN <<END_CONFIGURE sh 
git config --global user.name 'GitHub Action'
git config --global user.email 'chrispyduck@users.noreply.github.com'
END_CONFIGURE

# clone gh-pages branch and replace contents with newly build page
ARG GH_TOKEN
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" /tmp/skipcache
RUN git clone --depth 1 --branch gh-pages https://x-access-token:${GH_TOKEN}@github.com/chrispyduck/haiku.git
RUN rm -rf *
COPY --from=jekyll-build /work/_site .

# see if anything changed
RUN <<END_PUSH sh
if [[ $(git status --porcelain) ]]; then 
  echo "Changes detected. Publishing."
  git add -A
  git commit -m "automatic publish"
  git push
else 
  echo "No changes detected. All done!"
fi
END_PUSH
