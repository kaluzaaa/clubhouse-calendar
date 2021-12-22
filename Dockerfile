FROM ruby:2
WORKDIR /src
COPY Gemfile .
COPY Gemfile.lock .
RUN bundle install