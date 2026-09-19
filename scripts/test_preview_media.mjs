import assert from 'node:assert/strict';
import { test } from 'node:test';
import { byteRange, previewServer } from './preview-media.mjs';

test('bounded, open-ended, suffix and invalid ranges', () => {
  assert.deepEqual(byteRange('bytes=10-20', 100), { start: 10, end: 20 });
  assert.deepEqual(byteRange('bytes=90-', 100), { start: 90, end: 99 });
  assert.deepEqual(byteRange('bytes=-5', 100), { start: 95, end: 99 });
  for (const value of ['bytes=200-', 'bytes=20-10', 'bytes=-0', 'bytes=-', 'bytes=1-2,4-5']) {
    assert.equal(byteRange(value, 100), null);
  }
});

test('HTTP media supports seeking without exposing other files', async () => {
  const server = await previewServer({ port: 0 });
  try {
    const base = `http://127.0.0.1:${server.address().port}`;
    const response = await fetch(`${base}/media/goai_yungu_vln_overview_v2_64s.mp4`, { headers: { Range: 'bytes=4000000-4001023' } });
    assert.equal(response.status, 206);
    assert.equal(response.headers.get('accept-ranges'), 'bytes');
    assert.equal((await response.arrayBuffer()).byteLength, 1024);
    const escape = await fetch(`${base}/media/..%5C..%5Cpackage.json`);
    assert.equal(escape.status, 403);
  } finally {
    server.closeAllConnections();
    await new Promise(resolve => server.close(resolve));
  }
});
