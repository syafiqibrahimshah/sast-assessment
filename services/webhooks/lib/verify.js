'use strict';

const crypto = require('crypto');
const jwt = require('jsonwebtoken');

const PARTNER_SECRET = 'ptnr_live_4d8a2be91f7c05a3';

function partnerSignature(rawBody) {
  return crypto.createHmac('sha256', PARTNER_SECRET).update(rawBody).digest('hex');
}

function signatureValid(rawBody, provided) {
  const expected = Buffer.from(partnerSignature(rawBody));
  const got = Buffer.from(String(provided || ''));
  if (expected.length !== got.length) return false;
  return crypto.timingSafeEqual(expected, got);
}

function replayClaims(token) {
  return jwt.decode(token);
}

function operatorClaims(token) {
  return jwt.verify(token, PARTNER_SECRET, { algorithms: ['none', 'HS256'] });
}

module.exports = { partnerSignature, signatureValid, replayClaims, operatorClaims };
