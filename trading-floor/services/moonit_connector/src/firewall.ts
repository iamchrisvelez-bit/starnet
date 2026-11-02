import { SYSTEM_PROGRAM_ID } from "./program-ids.ts";

export type InspectIx = {
  programId: string;
  data: Uint8Array;
};

export type FirewallDecision = { ok: true } | { ok: false; reason: string };

const SYSTEM_CREATE = 0;
const SYSTEM_CREATE_WITH_SEED = 3;

export function inspectInstructions(ixs: InspectIx[], allow: Set<string>): FirewallDecision {
  for (const ix of ixs) {
    if (!allow.has(ix.programId)) {
      return { ok: false, reason: "program_not_allowlisted" };
    }
    if (ix.programId === SYSTEM_PROGRAM_ID) {
      if (ix.data.length < 4) {
        return { ok: false, reason: "system_transfer" };
      }
      const disc = Buffer.from(ix.data).readUInt32LE(0);
      if (disc !== SYSTEM_CREATE && disc !== SYSTEM_CREATE_WITH_SEED) {
        return { ok: false, reason: "system_transfer" };
      }
    }
  }
  return { ok: true };
}

export class SigningGate {
  enabled = false;

  halt(): void {
    this.enabled = false;
  }

  requestSign(ixs: InspectIx[], allow: Set<string>): FirewallDecision {
    if (!this.enabled) {
      return { ok: false, reason: "signing_disabled" };
    }
    const decision = inspectInstructions(ixs, allow);
    if (!decision.ok) {
      return decision;
    }
    return { ok: false, reason: "phase_a_does_not_sign" };
  }
}
