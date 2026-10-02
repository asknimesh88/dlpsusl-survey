const fs=require('fs');
const html=fs.readFileSync('index.html','utf8');
fs.writeFileSync('worker.js',`// Cloudflare Worker: serves the Graduate Satisfaction Survey dashboard.
// Paste this whole file into the Worker's code editor (Edit code) and click Deploy.
const HTML = ${JSON.stringify(html)};

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname === "/favicon.ico") return new Response(null, { status: 204 });
    return new Response(HTML, {
      headers: {
        "content-type": "text/html; charset=utf-8",
        "cache-control": "public, max-age=300",
        "x-content-type-options": "nosniff",
      },
    });
  },
};
`);
console.log((fs.statSync('worker.js').size/1024).toFixed(0)+' KB');
