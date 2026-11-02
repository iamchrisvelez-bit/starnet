import { createServer, type IncomingMessage, type ServerResponse } from "node:http";

import { assertPhaseA } from "./client.ts";
import { SigningGate, type InspectIx } from "./firewall.ts";
import { allowlist } from "./program-ids.ts";

const gate = new SigningGate();

function readBody(req: IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on("data", (chunk) => chunks.push(Buffer.from(chunk)));
    req.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
    req.on("error", reject);
  });
}

function send(res: ServerResponse, status: number, body: unknown): void {
  const raw = JSON.stringify(body);
  res.writeHead(status, { "content-type": "application/json" });
  res.end(raw);
}

export function start(port = Number(process.env.PORT ?? 8090)) {
  assertPhaseA();
  const server = createServer(async (req, res) => {
    const url = req.url ?? "/";
    if (req.method === "GET" && url === "/internal/health") {
      send(res, 200, {
        rpc: "devnet",
        phase: "A",
        signing_enabled: gate.enabled,
        key_loaded: Boolean(process.env.SOLANA_HOT_WALLET_PRIVATE_KEY),
      });
      return;
    }
    if (req.method === "POST" && url === "/internal/halt") {
      gate.halt();
      send(res, 200, { signing_enabled: false });
      return;
    }
    if (req.method === "GET" && url === "/internal/positions") {
      send(res, 200, { positions: [] });
      return;
    }
    if (req.method === "POST" && url === "/internal/quote") {
      send(res, 200, { signed: false });
      return;
    }
    if (req.method === "POST" && url === "/internal/order") {
      const raw = await readBody(req);
      const body = raw
        ? (JSON.parse(raw) as {
            risk_token?: string;
            compliance_token?: string;
            instructions?: { programId: string; data_base64?: string }[];
          })
        : {};
      if (!body.risk_token || !body.compliance_token) {
        send(res, 403, { ok: false, reason: "missing_token", signed: false });
        return;
      }
      const ixs: InspectIx[] = (body.instructions ?? []).map((ix) => ({
        programId: ix.programId,
        data: Buffer.from(ix.data_base64 ?? "", "base64"),
      }));
      const decision = gate.requestSign(ixs, allowlist());
      send(res, decision.ok ? 200 : 403, { ...decision, signed: false });
      return;
    }
    send(res, 404, { ok: false });
  });
  return new Promise<ReturnType<typeof createServer>>((resolve) => {
    server.listen(port, "0.0.0.0", () => resolve(server));
  });
}

if (process.argv[1] && process.argv[1].endsWith("server.ts")) {
  start().catch((error: unknown) => {
    const message = error instanceof Error ? error.message : "start failed";
    process.stderr.write(`${message}\n`);
    process.exit(1);
  });
}
