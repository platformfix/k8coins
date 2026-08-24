// Adapted from jpetazzo/container.training's dockercoins/webui/webui.js
// (Apache 2.0). See NOTICE.
import express from 'express';
import morgan from 'morgan';
import { createClient } from 'redis';
import promClient from 'prom-client';

promClient.collectDefaultMetrics();
var jsonRequests = new promClient.Counter({
    name: 'k8coins_webui_json_requests_total',
    help: 'Total requests to /json'
});

var client = await createClient({
  url: "redis://redis",
  socket: {
    family: 0
  }
})
    .on("error", function (err) {
        console.error("Redis error", err);
    })
    .connect();

var app = express();

app.use(morgan('common'));

app.get('/', function (req, res) {
    res.redirect('/index.html');
});

// Deliberately does not check redis connectivity: webui is designed to keep
// serving its last-known counts when a dependency is down (see the README's
// failure-isolation note), so its own health is not the same question as
// "is redis reachable right now."
app.get('/healthz', function (req, res) {
    res.send('ok\n');
});

app.get('/live', function (req, res) {
    res.send('ok\n');
});

app.get('/metrics', async function (req, res) {
    res.set('Content-Type', promClient.register.contentType);
    res.send(await promClient.register.metrics());
});

app.get('/json', async(req, res) => {
    jsonRequests.inc();
    var coins = await client.hLen('wallet');
    var hashes = await client.get('hashes');
    var now = Date.now() / 1000;
    res.json({
        coins: coins,
        hashes: hashes,
        now: now
    });
});

app.use(express.static('files'));

var server = app.listen(80, function () {
    console.log('WEBUI running on port 80');
});
