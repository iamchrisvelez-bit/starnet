import assert from "node:assert/strict";
import { test } from "node:test";
import { createRequire } from "node:module";

import { inspectInstructions, SigningGate } from "../src/firewall.ts";
import { allowlist, MOONIT_PROGRAM_ID, SYSTEM_PROGRAM_ID } from "../src/program-ids.ts";
import { assertPhaseA, createMoonitClient } from "../src/client.ts";

const require = createRequire(import.meta.url);
const web3 = require("@solana/web3.js") as typeof import("@solana/web3.js");

function asIx(ix: { programId: { toBase58(): string }; data: Buffer | Uint8Array }) {
  return { programId: ix.programId.toBase58(), data: new Uint8Array(ix.data) };
}

test("program id outside the allowlist is refused", () => {
  const decision = inspectInstructions(
    [{ programId: "11111111111111111111111111111112", data: new Uint8Array([0, 0, 0, 0]) }],
    allowlist(),
  );
  assert.equal(decision.ok, false);
  if (!decision.ok) assert.equal(decision.reason, "program_not_allowlisted");
});

test("system transfer to an outside address is refused", () => {
  const desk = web3.Keypair.generate();
  const outsider = web3.Keypair.generate();
  const ix = web3.SystemProgram.transfer({
    fromPubkey: desk.publicKey,
    toPubkey: outsider.publicKey,
    lamports: 1,
  });
  const decision = inspectInstructions([asIx(ix)], allowlist());
  assert.equal(decision.ok, false);
  if (!decision.ok) assert.equal(decision.reason, "system_transfer");
});

test("system create account and compute budget pass the firewall", () => {
  const payer = web3.Keypair.generate();
  const created = web3.Keypair.generate();
  const create = web3.SystemProgram.createAccount({
    fromPubkey: payer.publicKey,
    newAccountPubkey: created.publicKey,
    lamports: 1_000_000,
    space: 0,
    programId: web3.SystemProgram.programId,
  });
  const budget = web3.ComputeBudgetProgram.setComputeUnitPrice({ microLamports: 1 });
  const decision = inspectInstructions([asIx(create), asIx(budget)], allowlist());
  assert.equal(decision.ok, true);
});

test("halt refuses a sign attempt immediately", () => {
  const gate = new SigningGate();
  gate.enabled = true;
  const started = Date.now();
  gate.halt();
  const decision = gate.requestSign([], allowlist());
  assert.ok(Date.now() - started < 1000);
  assert.equal(decision.ok, false);
  if (!decision.ok) assert.equal(decision.reason, "signing_disabled");
});

test("phase A skeleton does not sign even when the gate is open", () => {
  const gate = new SigningGate();
  gate.enabled = true;
  const decision = gate.requestSign(
    [{ programId: MOONIT_PROGRAM_ID, data: new Uint8Array([1]) }],
    allowlist(),
  );
  assert.equal(decision.ok, false);
  if (!decision.ok) assert.equal(decision.reason, "phase_a_does_not_sign");
});

test("mainnet and a missing firewall refuse startup", () => {
  const previous = process.env.MOONIT_ENVIRONMENT;
  const firewall = process.env.SIGNING_FIREWALL;
  process.env.MOONIT_ENVIRONMENT = "MAINNET";
  assert.throws(() => assertPhaseA(), /devnet only/);
  process.env.MOONIT_ENVIRONMENT = "DEVNET";
  process.env.SIGNING_FIREWALL = "off";
  assert.throws(() => assertPhaseA(), /signing_firewall/);
  if (firewall === undefined) delete process.env.SIGNING_FIREWALL;
  else process.env.SIGNING_FIREWALL = firewall;
  if (previous === undefined) delete process.env.MOONIT_ENVIRONMENT;
  else process.env.MOONIT_ENVIRONMENT = previous;
  const client = createMoonitClient("https://api.devnet.solana.com");
  assert.ok(client);
});

test("moonit program id matches the installed SDK", () => {
  const sdk = require("@moonit/sdk") as { programId: { toBase58(): string } };
  assert.equal(MOONIT_PROGRAM_ID, sdk.programId.toBase58());
  assert.equal(MOONIT_PROGRAM_ID, "MoonCVVNZFSYkqNXP6bxHLPL6QQJiMagDL3qcqUQTrG");
  assert.equal(SYSTEM_PROGRAM_ID, "11111111111111111111111111111111");
});
