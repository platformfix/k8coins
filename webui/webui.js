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
  password: process.env.REDIS_PASSWORD,
  socket: {
    family: 0
  }
})
    .on("error", function (err) {
        console.error("Redis error", err);
    })
    .connect();

// Wallet size is read from redis at scrape time rather than counted here:
// unlike worker's k8coins_coins_total, it survives process restarts. If
// redis can't answer within a second, the coin sample is dropped for that
// scrape (rather than repeating a stale number that looks current) and
// k8coins_wallet_up reports 0 - so /metrics itself never fails or hangs
// because redis is down. prom-client collects metrics concurrently, so both
// gauges await one shared read (null on failure) per scrape. The timeout is
// a race rather than node-redis's abortSignal, because that signal stops
// applying once a command is on the socket - so it can't bound a redis that
// accepted the connection but stopped answering.
var walletRead = null;
function readWallet() {
    walletRead ??= Promise.race([
        client.hLen('wallet'),
        new Promise((_, reject) => setTimeout(reject, 1000, new Error('redis read timed out')))
    ])
        .catch(() => null)
        .finally(() => { walletRead = null; });
    return walletRead;
}
new promClient.Gauge({
    name: 'k8coins_wallet_coins',
    help: 'Coins currently in the redis wallet (absent while redis is unreadable)',
    async collect() {
        var coins = await readWallet();
        if (coins === null) {
            this.remove();
        } else {
            this.set(coins);
        }
    }
});
new promClient.Gauge({
    name: 'k8coins_wallet_up',
    help: 'Whether webui could read the redis wallet on this scrape (1) or not (0)',
    async collect() {
        this.set(await readWallet() === null ? 0 : 1);
    }
});

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
