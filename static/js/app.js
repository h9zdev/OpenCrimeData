const form = document.getElementById('searchForm');
const localResults = document.getElementById('localResults');
const sourceResults = document.getElementById('sourceResults');
const linkResults = document.getElementById('linkResults');

function renderObjectRow(key, value) {
  return `<div><strong>${key}:</strong> ${value ?? ''}</div>`;
}

function renderResults(data) {
  localResults.innerHTML = data.local_results.length
    ? data.local_results
        .map(
          (record) =>
            `<div class="result-item">${Object.entries(record)
              .map(([k, v]) => renderObjectRow(k, v))
              .join('')}</div>`
        )
        .join('')
    : '<div class="result-item">No local records found.</div>';

  sourceResults.innerHTML = data.source_snapshots
    .map(
      (s) => `<div class="result-item">
        <div><strong>Source:</strong> ${s.source}</div>
        <div><strong>Status:</strong> ${s.status}</div>
        <pre>${JSON.stringify(s, null, 2)}</pre>
      </div>`
    )
    .join('');

  linkResults.innerHTML = Object.entries(data.web_links)
    .map(
      ([name, url]) => `<div class="result-item"><a href="${url}" target="_blank">${name}</a></div>`
    )
    .join('');
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const params = new URLSearchParams(new FormData(form));
  const response = await fetch(`/api/search?${params.toString()}`);
  const data = await response.json();
  renderResults(data);
});

fetch('/api/sources')
  .then((r) => r.json())
  .then((data) => {
    sourceResults.innerHTML = data.sources
      .map((s) => `<div class="result-item"><strong>${s.source}</strong>: ${s.status}</div>`)
      .join('');
  });
