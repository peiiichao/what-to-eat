const ALLOWED_ORIGINS = ['https://peiiichao.github.io', 'http://localhost:8765'];
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36';

function cors(origin) {
  return {
    'Access-Control-Allow-Origin': ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0],
    'Vary': 'Origin',
  };
}

function reply(body, status, origin) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8', ...cors(origin) },
  });
}

// Only Google Maps share links are fetched, so the worker can't be used as an open proxy.
function isMapsUrl(u) {
  return u.protocol === 'https:' && (u.hostname === 'maps.app.goo.gl' || u.hostname === 'www.google.com' || u.hostname === 'goo.gl') ;
}

export default {
  async fetch(request, env, ctx) {
    const origin = request.headers.get('Origin') || '';
    if (request.method === 'OPTIONS') return new Response(null, { headers: { ...cors(origin), 'Access-Control-Allow-Methods': 'GET' } });
    if (origin && !ALLOWED_ORIGINS.includes(origin)) return reply({ error: 'forbidden' }, 403, origin);

    let link;
    try { link = new URL(new URL(request.url).searchParams.get('url')); } catch { return reply({ error: '連結格式不正確' }, 400, origin); }
    if (!isMapsUrl(link)) return reply({ error: '只支援 Google Maps 分享連結' }, 400, origin);

    const cache = caches.default;
    const cacheKey = new Request('https://cache.local/list?u=' + encodeURIComponent(link.href));
    const hit = await cache.match(cacheKey);
    if (hit) return new Response(hit.body, { status: 200, headers: { 'Content-Type': 'application/json; charset=utf-8', ...cors(origin) } });

    try {
      // Short links only redirect for non-browser clients; browser UAs get an interstitial page.
      const first = await fetch(link, { headers: { 'User-Agent': 'curl/8.7.1' }, redirect: 'manual' });
      const loc = first.headers.get('Location');
      if (!loc) return reply({ error: '無法解析這個短網址' }, 422, origin);
      // The list id is in the redirect target, so build the data URL directly instead of scraping the page (which Google serves inconsistently to Cloudflare).
      const idMatch = loc.match(/!2s([^!&?]+)/) || loc.match(/placelists\/list\/([^/?&]+)/);
      if (!idMatch) return reply({ error: '找不到清單 ID，請確認這是清單的分享連結。' }, 422, origin);
      const listId = decodeURIComponent(idMatch[1]);
      const path = 'https://www.google.com/maps/preview/entitylist/getlist?authuser=0&hl=zh-TW&gl=tw&pb=' + encodeURIComponent('!1m4!1s' + listId + '!2e1!3m1!1e1!2e2!3e2!4i1000!6m3!1sx!15i204459!28e2!16b1');
      // Google rate-limits Cloudflare's shared egress IPs intermittently, so retry a few times.
      let res;
      for (let attempt = 0; attempt < 4; attempt++) {
        res = await fetch(path, { headers: { 'User-Agent': 'curl/8.7.1' } });
        if (res.ok || res.status !== 429) break;
        await new Promise((r) => setTimeout(r, 600 * (attempt + 1)));
      }
      if (!res.ok) return reply({ error: res.status === 429 ? 'Google 暫時限制了請求，請稍後再試。' : '清單讀取失敗，請確認清單是「共用」狀態。' }, res.status === 429 ? 503 : 422, origin);
      const text = (await res.text()).replace(/^\)\]\}'\s*/, '');
      const raw = JSON.parse(text)[0];
      const places = (raw[8] || []).map((x) => {
        const d = x[1];
        const [lat, lon] = d[5].slice(2, 4);
        const cid = (BigInt(d[6][1]) + (1n << 64n)) % (1n << 64n);
        return { id: String(cid), name: x[2], address: d[4] || d[2] || '', lat, lon, url: 'https://www.google.com/maps?cid=' + cid };
      }).filter((p) => Number.isFinite(p.lat) && Number.isFinite(p.lon));
      const out = reply({ listName: raw[4] || '', total: places.length, places }, 200, origin);
      ctx.waitUntil(cache.put(cacheKey, new Response(JSON.stringify({ listName: raw[4] || '', total: places.length, places }), { headers: { 'Cache-Control': 'max-age=3600' } })));
      return out;
    } catch (err) {
      return reply({ error: '讀取清單失敗：' + (err && err.message || err) }, 502, origin);
    }
  },
};
