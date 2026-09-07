# Adapted from jpetazzo/container.training's dockercoins/hasher/hasher.rb
# (Apache 2.0). See NOTICE.
require 'digest'
require 'sinatra'
require 'socket'
require 'prometheus/client'
require 'prometheus/client/formats/text'

set :port, 80
set :bind, '0.0.0.0'
# Internal-only service, no browser-facing exposure, so the DNS-rebinding
# attack this guards against doesn't apply here. Matches Sinatra's own
# production-mode default, applied explicitly so it also covers dev mode.
set :host_authorization, permitted_hosts: []

# Deliberate delay simulating "a little bit of work" - see docs/architecture.md.
# Configurable so a delivery can tune the pacing without rebuilding the image.
SLEEP_SECONDS = ENV.fetch('SLEEP_SECONDS', '0.1').to_f

prometheus = Prometheus::Client.registry
hashes_total = Prometheus::Client::Counter.new(
    :k8coins_hasher_hashes_total, docstring: 'Total hashes computed')
prometheus.register(hashes_total)

post '/' do
    # Simulate a bit of delay
    sleep SLEEP_SECONDS
    content_type 'text/plain'
    request.body.rewind
    hashes_total.increment
    "#{Digest::SHA2.new().update(request.body.read)}"
end

get '/' do
    "HASHER running on #{Socket.gethostname}\n"
end

get '/healthz' do
    # hasher has no external dependencies, so it is healthy whenever the
    # process is up and answering requests at all.
    "ok\n"
end

get '/live' do
    "ok\n"
end

get '/metrics' do
    content_type 'text/plain'
    Prometheus::Client::Formats::Text.marshal(prometheus)
end
