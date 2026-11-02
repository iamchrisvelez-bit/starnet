"""Read-only config load. Limits come from config/risk.yaml and nowhere else."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

import yaml

REQUIRED_ISSUERS = (
    "LVMH Moët Hennessy Louis Vuitton",
    "Christian Dior SE",
)


def trading_floor_root() -> Path:
    override = os.environ.get("TF_ROOT")
    if override:
        return Path(override)
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "config" / "risk.yaml").is_file():
            return parent
    raise FileNotFoundError("config/risk.yaml not found")


@dataclass(frozen=True)
class FloorConfig:
    root: Path
    risk: dict
    risk_yaml_sha256: str
    restricted: dict
    approvals: dict
    venues: dict
    symbols: dict
    fees: dict
    slippage: dict


def _read_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise SystemExit(f"Refusing to start: {path.name} is not a mapping")
    return loaded


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_restricted_seeds(restricted: dict) -> None:
    issuers = restricted.get("issuers") or []
    names = {str(item.get("name", "")).casefold() for item in issuers if isinstance(item, dict)}
    for seed in REQUIRED_ISSUERS:
        if seed.casefold() not in names:
            raise SystemExit(f"Refusing to start: restricted list is missing {seed}")


def load_floor(root: Path | None = None) -> FloorConfig:
    base = root or trading_floor_root()
    config_dir = base / "config"
    risk_path = config_dir / "risk.yaml"
    restricted = _read_yaml(config_dir / "restricted.yaml")
    assert_restricted_seeds(restricted)
    risk = _read_yaml(risk_path)
    if risk.get("crypto", {}).get("leverage") != 1:
        raise SystemExit("Refusing to start: crypto.leverage must be 1")
    if risk.get("equities", {}).get("leverage") != 1:
        raise SystemExit("Refusing to start: equities.leverage must be 1")
    return FloorConfig(
        root=base,
        risk=risk,
        risk_yaml_sha256=file_sha256(risk_path),
        restricted=restricted,
        approvals=_read_yaml(config_dir / "approvals.yaml"),
        venues=_read_yaml(config_dir / "venues.yaml"),
        symbols=_read_yaml(config_dir / "symbols.yaml"),
        fees=_read_yaml(config_dir / "fees.yaml"),
        slippage=_read_yaml(config_dir / "slippage.yaml"),
    )
