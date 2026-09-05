import test from "node:test";
import assert from "node:assert/strict";

import worker from "../src/index.js";

test("rejects requests for another hostname", async () => {
  const response = await worker.fetch(
    new Request("https://example.com/"),
    { TREADJOY_ORIGIN_SHARED_SECRET: "synthetic-secret" },
  );

  assert.equal(response.status, 404);
});

test("fails closed when the origin secret is absent", async () => {
  const response = await worker.fetch(
    new Request("https://research.tread-joy.com/"),
    {},
  );

  assert.equal(response.status, 503);
});

test("adds the origin lock while preserving the Access JWT header", async () => {
  const originalFetch = globalThis.fetch;
  let forwardedRequest;
  globalThis.fetch = async (request) => {
    forwardedRequest = request;
    return new Response("ok", { status: 200 });
  };

  try {
    const response = await worker.fetch(
      new Request("https://research.tread-joy.com/", {
        headers: { "Cf-Access-Jwt-Assertion": "synthetic-jwt" },
      }),
      { TREADJOY_ORIGIN_SHARED_SECRET: "synthetic-secret" },
    );

    assert.equal(response.status, 200);
    assert.equal(
      forwardedRequest.headers.get("X-TreadJoy-Origin"),
      "synthetic-secret",
    );
    assert.equal(
      forwardedRequest.headers.get("Cf-Access-Jwt-Assertion"),
      "synthetic-jwt",
    );
  } finally {
    globalThis.fetch = originalFetch;
  }
});
