import assert from "node:assert/strict";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { test } from "node:test";

const SRC = join(import.meta.dirname, "..", "src");
const BANNED = /\b(prepareMintTx|submitMintTx|tokenMint|launchToken|mintToken|migrateFunds)\b/;
const JUPITER_API = /api\.jup\.ag/;

function files(dir: string): string[] {
  const found: string[] = [];
  for (const name of readdirSync(dir)) {
    const path = join(dir, name);
    if (statSync(path).isDirectory()) {
      found.push(...files(path));
    } else if (name.endsWith(".ts")) {
      found.push(path);
    }
  }
  return found;
}

test("connector source has no mint, launch, or Jupiter swap call", () => {
  const paths = files(SRC);
  assert.ok(paths.length > 0);
  for (const path of paths) {
    const text = readFileSync(path, "utf8");
    assert.equal(BANNED.test(text), false, path);
    assert.equal(JUPITER_API.test(text), false, path);
  }
});
