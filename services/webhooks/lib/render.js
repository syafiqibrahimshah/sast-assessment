'use strict';

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function receiptRow(partner, reference) {
  return `<tr><td>${escapeHtml(partner)}</td><td>${escapeHtml(reference)}</td></tr>`;
}

function errorPanel(partner, message) {
  return `<div class="panel"><h3>${partner}</h3><pre>${message}</pre></div>`;
}

module.exports = { escapeHtml, receiptRow, errorPanel };
