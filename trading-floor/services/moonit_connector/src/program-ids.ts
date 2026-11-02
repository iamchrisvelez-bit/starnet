/**
 * Program ids loaded from the installed libraries.
 * Doc revision 2026-11-02:
 * - @moonit/sdk 1.3.0 `programId` (IDL address, not a handwritten guess)
 * - @solana/web3.js 1.95.8 SystemProgram and ComputeBudgetProgram
 * - @solana/spl-token 0.3.9 TOKEN_PROGRAM_ID, TOKEN_2022_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
 * - Jupiter V6 id is the example value labeled "Jupiter V6" at
 *   https://dev.jup.ag/api-reference/swap/v1/program-id-to-label
 *   Swap API V2 (https://dev.jup.ag/docs/swap/v2/build, retrieved 2026-11-02)
 *   does not publish a different program id. Phase A does not call Jupiter.
 */
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const sdk = require("@moonit/sdk") as { programId: { toBase58(): string } };
const web3 = require("@solana/web3.js") as {
  SystemProgram: { programId: { toBase58(): string } };
  ComputeBudgetProgram: { programId: { toBase58(): string } };
};
const spl = require("@solana/spl-token") as {
  TOKEN_PROGRAM_ID: { toBase58(): string };
  TOKEN_2022_PROGRAM_ID: { toBase58(): string };
  ASSOCIATED_TOKEN_PROGRAM_ID: { toBase58(): string };
};

export const MOONIT_PROGRAM_ID = sdk.programId.toBase58();
export const SYSTEM_PROGRAM_ID = web3.SystemProgram.programId.toBase58();
export const COMPUTE_BUDGET_PROGRAM_ID = web3.ComputeBudgetProgram.programId.toBase58();
export const TOKEN_PROGRAM = spl.TOKEN_PROGRAM_ID.toBase58();
export const TOKEN_2022_PROGRAM = spl.TOKEN_2022_PROGRAM_ID.toBase58();
export const ASSOCIATED_TOKEN_PROGRAM = spl.ASSOCIATED_TOKEN_PROGRAM_ID.toBase58();

/** Documented Jupiter V6 id. Phase A never calls the Swap API. */
export const JUPITER_V6_PROGRAM_ID = "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4";

export function allowlist(): Set<string> {
  return new Set([
    MOONIT_PROGRAM_ID,
    SYSTEM_PROGRAM_ID,
    COMPUTE_BUDGET_PROGRAM_ID,
    TOKEN_PROGRAM,
    TOKEN_2022_PROGRAM,
    ASSOCIATED_TOKEN_PROGRAM,
    JUPITER_V6_PROGRAM_ID,
  ]);
}
