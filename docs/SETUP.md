# One-time setup

## 1. Postman

1. Create (or pick) a Postman **workspace** for the demo. Copy its ID from the workspace URL or settings.
2. In Postman, generate an **API key** (Settings > API keys). Treat it as a secret.
3. Configure the workspace's **API governance rules** (the OWASP ruleset) so `postman spec lint` has rules to apply. Availability of governance rules depends on your Postman plan, so confirm it in your workspace.
4. Create the first spec in **Spec Hub** and copy its **spec ID**:
   - UI: Spec Hub > Import > upload `specs/customer-account-management-api/customer-account-management-api.yaml`, or
   - CLI helper (see step 4 below).

## 2. GitHub repo

1. Create a new repo and push the contents of this folder to `main`.
2. Settings > Secrets and variables > Actions:
   - **Secret** `POSTMAN_API_KEY` = your Postman API key
   - **Variable** `POSTMAN_WORKSPACE_ID` = your workspace ID
3. (Recommended) Settings > Branches > protect `main`, require pull requests, and require the
   **Validate API specifications** check. This is what makes "a failing spec never reaches Postman" true.

## 3. Wire the spec ID

Replace `REPLACE-WITH-POSTMAN-SPEC-ID` for `customer-account-management-api` in:

- `.postman/api-mappings.yaml`
- `governance/catalogue.json`

Keep the indentation in the mappings file exactly as is. The detect script parses it line by line.

## 4. Optional: create specs in Postman from the command line

```bash
export POSTMAN_API_KEY=...
export POSTMAN_WORKSPACE_ID=...
python scripts/create-postman-spec.py customer-account-management-api
```

This calls the Postman API to create the spec and writes the ID into both files. It has not been tested against a live
workspace. If it errors, use the Postman UI import instead.

## 5. First run

Commit and push to `main`. Because `customer-account-management-api` has a spec but no collection yet, the reconcile step adds it to the
matrix, and the workflow generates and syncs its first collection. Check the Actions run, then open the workspace in Postman.

## Local checks (no Postman needed)

```bash
npm install -g @stoplight/spectral-cli
spectral lint --ruleset .spectral-owasp.yaml specs/**/*.yaml
python scripts/validate-governance.py
bash scripts/demo-governance.sh
```

## Adding a new API

```bash
python scripts/onboard-api.py card-management-api \
  --display-name "Card Management API" --domain "Card Services" \
  --owner "Cards API Team" --description "Card management endpoints"
python scripts/create-postman-spec.py card-management-api   # or import in Postman and edit the mapping by hand
```

Then open a PR. A changed spec with no entry in `.postman/api-mappings.yaml` fails detection on purpose.
