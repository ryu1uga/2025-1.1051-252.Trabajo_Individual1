// api/index.js
const express = require('express');
const morgan = require('morgan');
const redis = require('redis');

const app = express();
app.use(express.json());

// Simple JSON logger middleware
app.use((req, res, next) => {
  req.startTime = Date.now();
  next();
});

app.use(morgan('dev'));

const REDIS_URL = process.env.REDIS_URL || 'redis://redis:6379';
const publisher = redis.createClient({ url: REDIS_URL });
publisher.connect().catch(e => console.error('redis conn', e));

function publishEvent(evt) {
  // publish structured event to "events" channel
  publisher.publish('events', JSON.stringify(evt)).catch(console.error);
}

app.get('/api/v1/items', (req, res) => {
  const evt = {
    ts: new Date().toISOString(),
    path: req.path,
    method: req.method,
    client_ip: req.ip,
    ua: req.get('user-agent'),
    code: 200
  };
  publishEvent({...evt, type: 'request'});
  res.json({ items: [1,2,3] });
});

// Canary endpoint (should never be used by legit clients)
app.get('/api/v1/.canary/FLAG_ABC123', (req, res) => {
  const evt = {
    ts: new Date().toISOString(),
    path: req.path,
    method: req.method,
    client_ip: req.ip,
    ua: req.get('user-agent'),
    type: 'canary'
  };
  publishEvent(evt);
  // return fake data so attacker doesn't immediately know it's a trap
  res.json({ message: 'ok' });
});

// Example protected endpoint causing 401 if no header
app.get('/api/v1/admin', (req, res) => {
  const auth = req.get('x-api-key') || '';
  const evt = {
    ts: new Date().toISOString(),
    path: req.path,
    method: req.method,
    client_ip: req.ip,
    ua: req.get('user-agent'),
  };
  if (auth !== 'SECRET_ADMIN_KEY') {
    evt.type = 'auth_fail';
    evt.code = 401;
    publishEvent(evt);
    return res.status(401).json({ error: 'unauthorized' });
  }
  evt.type = 'auth_ok';
  evt.code = 200;
  publishEvent(evt);
  res.json({ admin: true });
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log('API listening', port));