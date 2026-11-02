# Console API

Read token cannot call command routes. There is no external order endpoint.
Web and Telegram show the mode. They cannot flip `PAPER` to `LIVE`.

| Method | Path | Auth |
| --- | --- | --- |
| GET | `/api/v1/mode` | read |
| GET | `/api/v1/floor` | read |
| GET | `/api/v1/desks` | read |
| GET | `/api/v1/positions` | read |
| GET | `/api/v1/orders` | read |
| GET | `/api/v1/fills` | read |
| GET | `/api/v1/approvals` | read |
| GET | `/api/v1/guards` | read |
| GET | `/api/v1/equity` | read |
| POST | `/api/v1/commands/kill` | command |
| POST | `/api/v1/commands/pause` | command |
| POST | `/api/v1/commands/resume` | command |
| WS | `/api/v1/stream` | read. First event is `mode`. |

`/resume` clears a manual pause. It does not clear KILL.
