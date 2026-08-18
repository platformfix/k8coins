FROM ruby:4.0-alpine AS builder
WORKDIR /app
RUN apk add --no-cache build-base=0.5-r4
COPY Gemfile Gemfile.lock ./
RUN bundle config set --local deployment 'true' && bundle install

FROM ruby:4.0-alpine
WORKDIR /app
RUN addgroup -g 1000 -S app && adduser -u 1000 -S app -G app
COPY --from=builder /app/vendor/bundle vendor/bundle
COPY --from=builder /usr/local/bundle /usr/local/bundle
COPY Gemfile Gemfile.lock hasher.rb ./
USER 1000
EXPOSE 80
HEALTHCHECK --interval=10s --timeout=3s CMD ["wget", "-q", "-O-", "http://127.0.0.1:80/"]
CMD ["bundle", "exec", "ruby", "hasher.rb"]
