import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const projectRoot = join(dirname(fileURLToPath(import.meta.url)), "..");
const publicRoot = join(projectRoot, "public");

const requiredFiles = [
  ".node-version",
  "package.json",
  "package-lock.json",
  "wrangler.jsonc",
  "public/index.html",
  "public/404.html",
  "public/styles.css",
  "public/_headers",
  "public/robots.txt",
];

async function text(relativePath) {
  return readFile(join(projectRoot, relativePath), "utf8");
}

function visibleText(html) {
  return html
    .replace(/<head[\s\S]*?<\/head>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function assertNoActiveOrExternalContent(html, filename) {
  assert.doesNotMatch(html, /<(?:script|form|iframe|img|picture|video|audio|source|object|embed)\b/i, filename);
  assert.doesNotMatch(html, /\b(?:src|action)\s*=\s*["'][^"']+["']/i, filename);
  assert.doesNotMatch(html, /(?:https?:)?\/\//i, filename);
  assert.doesNotMatch(html, /\b(?:analytics|gtag|googletagmanager|pixel|segment|hotjar|tracking)\b/i, filename);
}

test("all required deployment files are present", async () => {
  await Promise.all(requiredFiles.map((relativePath) => text(relativePath)));
});

test("the holding page contains only the approved visible copy", async () => {
  const html = await text("public/index.html");
  assert.equal(
    visibleText(html),
    "Coming Soon We’re building TreadJoy. Check back soon.",
  );
  assert.doesNotMatch(html, /class="brand"/);
  assert.match(html, /<title>TreadJoy \| Coming Soon<\/title>/);
  assert.match(html, /<link rel="canonical" href="https:\/\/tread-joy\.com\/">/);
  assert.match(html, /<meta name="robots" content="noindex, nofollow, noarchive">/);
  assertNoActiveOrExternalContent(
    html.replace('href="https://tread-joy.com/"', 'href="/"'),
    "index.html contains active or external content",
  );
});

test("the custom 404 is distinct, branded, and locally navigable", async () => {
  const html = await text("public/404.html");
  assert.match(html, /<title>Page Not Found \| TreadJoy<\/title>/);
  assert.match(html, /<p class="brand">TreadJoy<\/p>/);
  assert.match(html, /<h1 id="page-title">Page Not Found<\/h1>/);
  assert.match(html, /<a class="home-link" href="\/">Return Home<\/a>/);
  assert.match(html, /<meta name="robots" content="noindex, nofollow, noarchive">/);
  assertNoActiveOrExternalContent(html, "404.html contains active or external content");
});

test("the stylesheet uses approved colors and no remote resources or motion", async () => {
  const css = await text("public/styles.css");
  for (const color of ["#4ccbf0", "#eddc4f", "#191919", "#e9e1d5", "#dce5e7"]) {
    assert.match(css, new RegExp(color, "i"));
  }
  assert.doesNotMatch(css, /@import|url\s*\(|animation(?:-name)?\s*:|transition\s*:/i);
  assert.match(css, /--color-page:\s*#fff/i);
  assert.match(css, /block-size:\s*100dvh/i);
  assert.match(css, /letter-spacing:\s*-0\.06em/i);
  assert.match(css, /letter-spacing:\s*0\.015em/i);
  assert.match(css, /@media \(prefers-reduced-motion: reduce\)/);
  assert.match(css, /:focus-visible/);
});

test("the response policy is restrictive with staged HSTS", async () => {
  const headers = await text("public/_headers");
  const requiredHeaders = [
    "Content-Security-Policy:",
    "default-src 'none'",
    "style-src 'self'",
    "connect-src 'none'",
    "frame-ancestors 'none'",
    "form-action 'none'",
    "X-Content-Type-Options: nosniff",
    "X-Frame-Options: DENY",
    "Referrer-Policy: no-referrer",
    "Strict-Transport-Security: max-age=3600",
    "Permissions-Policy:",
    "X-Robots-Tag: noindex, nofollow, noarchive",
  ];
  for (const directive of requiredHeaders) assert.ok(headers.includes(directive), directive);
  assert.doesNotMatch(headers, /includeSubDomains|preload/i);
  assert.doesNotMatch(headers, /set-cookie/i);
});

test("robots.txt allows crawlers to observe the noindex response", async () => {
  assert.equal(await text("public/robots.txt"), "User-agent: *\nAllow: /\n");
});

test("Wrangler is asset-only and has no routes, bindings, variables, or secrets", async () => {
  const config = JSON.parse(await text("wrangler.jsonc"));
  assert.equal(config.name, "treadjoy-coming-soon");
  assert.equal(config.preview_urls, true);
  assert.deepEqual(config.assets, {
    directory: "./public",
    not_found_handling: "404-page",
    html_handling: "auto-trailing-slash",
  });
  for (const forbiddenKey of [
    "main",
    "route",
    "routes",
    "vars",
    "d1_databases",
    "hyperdrive",
    "kv_namespaces",
    "r2_buckets",
    "services",
    "queues",
  ]) {
    assert.equal(config[forbiddenKey], undefined, forbiddenKey);
  }
});

test("the Node and Wrangler versions are explicitly pinned", async () => {
  assert.match(await text(".node-version"), /^24\.\d+\.\d+\n$/);
  const packageJson = JSON.parse(await text("package.json"));
  assert.equal(packageJson.engines.node, ">=24 <25");
  assert.match(packageJson.devDependencies.wrangler, /^\d+\.\d+\.\d+$/);
  assert.doesNotMatch(packageJson.devDependencies.wrangler, /^[~^]/);
});

test("the public directory contains no unexpected deployable files", async () => {
  const { readdir } = await import("node:fs/promises");
  const files = (await readdir(publicRoot)).sort();
  assert.deepEqual(files, ["404.html", "_headers", "index.html", "robots.txt", "styles.css"]);
});
