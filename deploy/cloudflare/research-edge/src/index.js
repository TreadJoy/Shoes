const RESEARCH_HOSTNAME = "research.tread-joy.com";
const ORIGIN_HEADER = "X-TreadJoy-Origin";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.hostname !== RESEARCH_HOSTNAME) {
      return new Response("Not found", {
        status: 404,
        headers: { "Cache-Control": "no-store" },
      });
    }

    const originSecret = env.TREADJOY_ORIGIN_SHARED_SECRET;
    if (!originSecret) {
      return new Response("Configuration unavailable", {
        status: 503,
        headers: { "Cache-Control": "no-store" },
      });
    }

    // Access adds its signed JWT to the request before this Worker runs. Keep
    // that header intact and add only the private origin-lock header required
    // by Django. The secret is a Worker secret and never belongs in source.
    const headers = new Headers(request.headers);
    headers.set(ORIGIN_HEADER, originSecret);
    return fetch(new Request(request, { headers }));
  },
};
