# Audit report

```
verdict: fail
```

| Requirement | Evidence | Result |
| --- | --- | --- |
| Sold counts and sizes | checker output | pass or fail |
| Brief line | file and frame | pass or fail |

defects:

- `delivery/example.png`: replace the headline with the brief line "Refill ships Friday". The file currently says "Refill Friday".

A pass has `verdict: pass` and no defect lines. Copy this shape into `jobs/<id>/audit-report.md`. Do not leave this template filled in as if it were a job.
