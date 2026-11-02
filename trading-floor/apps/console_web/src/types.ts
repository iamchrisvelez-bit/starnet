export type ModePayload = {
  mode: "PAPER" | "LIVE";
  live_confirmed: boolean;
  halted: boolean;
  paused: boolean;
};
