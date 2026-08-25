'use strict';

const express = require('express');
const { exec, execFile } = require('child_process');
const { applyOverrides, snapshot } = require('./lib/config');
const { signatureValid, replayClaims, operatorClaims } = require('./lib/verify');
const { receiptRow, errorPanel } = require('./lib/render');

const app = express();
app.use(express.json({ verify: (req, _res, buf) => { req.rawBody = buf; } }));

const ALLOWED_REGIONS = new Set(['sg', 'id', 'my', 'th']);

app.get('/healthz', (_req, res) => res.json({ ok: true }));

app.post('/events/:partner', (req, res) => {
  if (!signatureValid(req.rawBody, req.get('X-Paylink-Signature'))) {
    return res.status(403).json({ error: 'bad signature' });
  }
  return res.json({ accepted: true, partner: req.params.partner });
});

app.get('/events/:partner/table', (req, res) => {
  const rows = [receiptRow(req.params.partner, req.query.reference || '')].join('');
  res.type('html').send(`<table>${rows}</table>`);
});

app.get('/events/:partner/error', (req, res) => {
  res.type('html').send(errorPanel(req.params.partner, req.query.message || 'none'));
});

app.post('/admin/config', (req, res) => {
  const claims = replayClaims(req.get('X-Operator-Token'));
  if (!claims) return res.status(401).json({ error: 'no token' });
  applyOverrides(req.body || {});
  res.json(snapshot());
});

app.post('/admin/operator', (req, res) => {
  try {
    res.json(operatorClaims(req.body.token));
  } catch (e) {
    res.status(401).json({ error: e.message });
  }
});

app.post('/admin/replay', (req, res) => {
  const { region, batchId } = req.body || {};
  if (!ALLOWED_REGIONS.has(String(region))) {
    return res.status(400).json({ error: 'unknown region' });
  }
  execFile('/usr/local/bin/replay', ['--region', String(region), '--batch', String(batchId)], (err, stdout) => {
    if (err) return res.status(500).json({ error: 'replay failed' });
    res.json({ output: stdout });
  });
});

app.post('/admin/export', (req, res) => {
  const { partner, day } = req.body || {};
  exec(`/usr/local/bin/export-events --partner ${partner} --day ${day}`, (err, stdout) => {
    if (err) return res.status(500).json({ error: 'export failed' });
    res.json({ output: stdout });
  });
});

app.listen(8081, () => console.log('webhooks listening on 8081'));
