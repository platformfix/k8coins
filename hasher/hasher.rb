# Adapted from jpetazzo/container.training's dockercoins/hasher/hasher.rb
# (Apache 2.0). See NOTICE.
require 'digest'
require 'sinatra'
require 'socket'

set :port, 80
set :bind, '0.0.0.0'
# Internal-only service, no browser-facing exposure, so the DNS-rebinding
# attack this guards against doesn't apply here. Matches Sinatra's own
# production-mode default, applied explicitly so it also covers dev mode.
set :host_authorization, permitted_hosts: []

post '/' do
    # Simulate a bit of delay
    sleep 0.1
    content_type 'text/plain'
    request.body.rewind
    "#{Digest::SHA2.new().update(request.body.read)}"
end

get '/' do
    "HASHER running on #{Socket.gethostname}\n"
end
