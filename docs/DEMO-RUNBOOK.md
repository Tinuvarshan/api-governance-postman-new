# Live demo runbook (about 5 minutes)

Matches the deck: slide 6 (OWASP rules), slide 8 (every push), slide 9 (end-to-end), slide 10 (two scenarios).

**Before you present:** setup done, `main` green, `customer-account-management-api` collection already exists in Postman,
GitHub Actions tab and Postman workspace open in two tabs.

---

## Demo 1: the catalogue approval gate (1 min, local)

```bash
python scripts/validate-governance.py
bash scripts/demo-governance.sh
```

Expected: first run prints `GOVERNANCE VALIDATION PASSED`. The script then shows an approved API passing and a
`Published` API with `approval_status: Pending` rejected (`Publication blocked; approval_status must be Approved`).

Say: a Published API must carry approval metadata, and CI enforces it.

## Demo 2: OWASP violation blocked on a PR (1.5 min)

```bash
git checkout -b demo/insecure-server
sed -i 's#https://api.example.com/v1#http://api.example.com/v1#' specs/customer-account-management-api/customer-account-management-api.yaml
git commit -am "Demo: switch server to http" && git push -u origin demo/insecure-server
```

Open a PR. In Actions, **Validate API specifications > Lint OpenAPI specifications** fails with `API governance requires HTTPS.`
The Postman jobs do not touch the cloud on a PR. **Leave this PR unmerged** as evidence.

Other violations you can try instead (each trips one rule):
- delete `security:` from the `get` operation: `Every operation must declare bearerAuth security.`
- change `scheme: bearer` to `scheme: basic` under `bearerAuth`: `Define components.securitySchemes.bearerAuth.`

## Demo 3: Scenario A, new API with no collection (1.5 min)

```bash
git checkout main && git pull && git checkout -b demo/new-card-management-api
python scripts/onboard-api.py card-management-api \
  --display-name "Card Management API" --domain "Card Services" \
  --owner "Cards API Team" --description "Card management endpoints"
python scripts/create-postman-spec.py card-management-api
```

Add one secured endpoint under `paths:` in `specs/card-management-api/card-management-api.yaml`:

```yaml
paths:
  /cards/{id}:
    get:
      summary: Get card
      security:
        - bearerAuth: []
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string }
      responses:
        "200": { description: Card returned }
        "401": { description: Unauthorized }
```

Commit, push, open PR (checks go green), merge. On `main` the workflow runs: lint, update the cloud spec,
generate the collection, discover it, sync. Show the new **card-management-api** collection in the Postman workspace.

## Demo 4: Scenario B, changed spec (1 min)

On a branch, add a second endpoint (or change a description) in `specs/customer-account-management-api/customer-account-management-api.yaml`, merge the PR.
In the run log show **Generate initial Postman collection** skipped, then **Synchronize** updating the existing collection.
In Postman, the collection now contains the new endpoint and was not recreated.

---

## If something goes wrong

| Symptom | Likely cause |
|---|---|
| `POSTMAN_API_KEY ... is not set` / HTTP 401 | secret missing or wrong name |
| `No Postman spec ID mapping for changed API` | add the API to `.postman/api-mappings.yaml` |
| `Found N collections named ...` | duplicate collections in Postman: delete extras, rerun |
| `Generated collection was not found` | generation is slow: rerun the workflow, or raise the retry count |
| `postman spec lint` fails on a spec that passes Spectral | the workspace ruleset is stricter; read the rule name in the log |
| PR run skips Postman jobs | no spec changed in that PR |

Rehearse once end to end the day before. Generation timing in Postman is the main thing that varies.
