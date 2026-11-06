# API Governance with Postman + GitHub Actions

OpenAPI specs live in Git as the source of truth. Every push and pull request is
checked against OWASP-aligned rules, and Postman Cloud specs and collections are
kept in sync automatically.

## How it works

| Step | What runs | Where |
|---|---|---|
| 1. Validate | Spectral lint (OWASP rules) on every spec + `validate-governance.py` catalogue/approval check | every PR and push |
| 2. Detect | `detect-changed-apis.py` finds changed specs (and, on `main`, APIs with no collection yet) | every PR and push |
| 3. Postman lint | `postman spec lint` against the workspace governance ruleset | every PR and push |
| 4. Update | `postman spec file update` pushes the changed spec to Postman Cloud | `main` only |
| 5. Generate | `postman spec generate collection` if no collection exists | `main` only |
| 6. Sync | `postman spec sync collection` keeps the collection aligned with the spec | `main` only |

Pull requests only run checks (read-only). Only pushes to `main` (or a manual run on `main`) change anything in Postman.

## Layout

```
.github/workflows/api-governance.yml   the pipeline
.spectral-owasp.yaml                   3 OWASP rules (HTTPS, bearer auth, secured operations)
.postman/api-mappings.yaml             specs/<name> -> Postman spec ID
governance/catalogue.json              owner, domain, lifecycle, approval metadata
specs/<name>/<name>.yaml               OpenAPI specs
templates/api-template.yaml            starter spec for new APIs
scripts/                               validate, detect, find collection, onboard, create Postman spec
tests/fixtures/                        approved vs pending catalogue samples for the local demo
docs/SETUP.md                          one-time setup
docs/DEMO-RUNBOOK.md                   step-by-step live demo with expected results
```

Start with `docs/SETUP.md`.
