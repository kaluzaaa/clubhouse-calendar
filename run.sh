#!/bin/bash

# set variable JEKYLL_GITHUB_TOKEN with your GH PAT, like export JEKYLL_GITHUB_TOKEN=589484746ffaac1aadbfd6f1XXX

rm -r -f _site
rm -r -f .sass-cache
docker rm -f dev-radio

docker build -t dev-radio.pl .

docker run --rm -it -p 4000:4000 -p 35729:35729 -v $(PWD):/src -e JEKYLL_GITHUB_TOKEN=$JEKYLL_GITHUB_TOKEN --name dev-radio dev-radio.pl bundle exec jekyll serve --drafts --future --watch --host=0.0.0.0 --livereload
