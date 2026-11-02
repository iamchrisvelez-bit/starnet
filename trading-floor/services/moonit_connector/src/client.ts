import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const sdk = require("@moonit/sdk") as {
  Environment: { DEVNET: string; MAINNET: string };
  Moonit: new (config: {
    rpcUrl: string;
    environment: string;
    chainOptions: { solana: { confirmOptions: { commitment: "confirmed" } } };
  }) => unknown;
};

const DEVNET_RPC = "https://api.devnet.solana.com";

export function assertPhaseA(): void {
  const phase = process.env.MOONIT_ENVIRONMENT ?? "DEVNET";
  if (phase !== "DEVNET") {
    throw new Error("Refusing to start: Moonit Phase A is devnet only");
  }
  if ((process.env.SIGNING_FIREWALL ?? "required") !== "required") {
    throw new Error("Refusing to start: signing_firewall must be required");
  }
}

export function createMoonitClient(rpcUrl: string = process.env.SOLANA_DEVNET_RPC_URL || DEVNET_RPC): unknown {
  assertPhaseA();
  return new sdk.Moonit({
    rpcUrl,
    environment: sdk.Environment.DEVNET,
    chainOptions: { solana: { confirmOptions: { commitment: "confirmed" } } },
  });
}
