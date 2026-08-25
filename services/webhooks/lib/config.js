'use strict';

const defaults = {
  retries: 3,
  backoffMs: 500,
  partners: {},
  features: { replay: false, strictSignature: true }
};

let live = JSON.parse(JSON.stringify(defaults));

function deepMerge(target, source) {
  for (const key of Object.keys(source)) {
    if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
      if (!target[key]) target[key] = {};
      deepMerge(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}

function applyOverrides(patch) {
  return deepMerge(live, patch);
}

function snapshot() {
  return live;
}

function reset() {
  live = JSON.parse(JSON.stringify(defaults));
}

module.exports = { applyOverrides, snapshot, reset, deepMerge };
