# syntax=docker/dockerfile-upstream:1.3.1-labs

ARG GCP_API_KEY
ARG GH_TOKEN

FROM docker.io/google/cloud-sdk:377.0.0-slim AS fetcher

WORKDIR /work

# install fetcher dependencies 
RUN pip3 install google-api-python-client google-auth-httplib2 google-auth-oauthlib pyyaml

# fetch data
ADD fetcher/fetch-haiku.py /work/fetcher/
ARG GCP_API_KEY
ENV GCP_API_KEY=${GCP_API_KEY}
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" /tmp/skipcache
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
set -eu 
git config --global user.name 'GitHub Action'
git config --global user.email 'chrispyduck@users.noreply.github.com'
mkdir -p ~/.ssh
ssh-keyscan github.com >> ~/.ssh/known_hosts
END_CONFIGURE

# clone gh-pages branch and replace contents with newly build page
ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" /tmp/skipcache
WORKDIR /work
#RUN --mount=type=secret,id=deploy_key,target=/root/.ssh/id_rsa <<END_CLONE sh
RUN --mount=type=ssh <<END_CLONE sh
git clone --depth 1 --branch gh-pages git@github.com:chrispyduck/haiku.git
END_CLONE
WORKDIR /work/haiku
RUN rm -rf *
COPY --from=jekyll-build /work/_site .

# see if anything changed
#RUN --mount=type=secret,id=deploy_key,target=/root/.ssh/id_rsa <<END_PUSH sh
RUN --mount=type=ssh <<END_PUSH sh
set -e
git add -A
git commit -m "automatic publish" && git push
END_PUSH
