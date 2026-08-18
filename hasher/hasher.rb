# Adapted from jpetazzo/container.training's dockercoins/hasher/hasher.rb
# (Apache 2.0). See NOTICE.
require 'digest'
require 'sinatra'
require 'socket'

set :port, 80
set :bind, '0.0.0.0'

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
