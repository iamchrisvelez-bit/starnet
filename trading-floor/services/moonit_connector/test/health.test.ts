import assert from "node:assert/strict";
import { test } from "node:test";

import { start } from "../src/server.ts";

test("health reports key_loaded and does not echo the key", async () => {
  process.env.MOONIT_ENVIRONMENT = "DEVNET";
  process.env.SIGNING_FIREWALL = "required";
  process.env.SOLANA_HOT_WALLET_PRIVATE_KEY = "CANARY_DO_NOT_LOG";
  const server = await start(0);
  const address = server.address();
  assert.ok(address && typeof address === "object");
  const response = await fetch(`http://127.0.0.1:${address.port}/internal/health`);
  const body = await response.json();
  assert.equal(body.phase, "A");
  assert.equal(body.key_loaded, true);
  assert.equal(JSON.stringify(body).includes("CANARY_DO_NOT_LOG"), false);
  const missing = await fetch(`http://127.0.0.1:${address.port}/internal/order`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ instructions: [] }),
  });
  const refused = await missing.json();
  assert.equal(refused.reason, "missing_token");
  assert.equal(refused.signed, false);
  server.close();
});
