# Workspace Guidance

## Deployment Model

The Vercel Git integration for `traveling-ketch` is intentionally **disconnected**, so a push to `master` never publishes to production by itself.

| Environment | How it deploys | Trigger |
|---|---|---|
| Production | `vercel --prod --yes` (manual) | Human runs the command |
| Preview (PR) | `.github/workflows/preview.yml` | Pull request opened or updated |
| Preview (local) | `vercel` (no `--prod`) | Human runs the command |

### Preview deployments

Pull requests get an automatic preview URL from `.github/workflows/preview.yml`, which comments the URL on the PR and writes it to the job summary. Previews are protected by Vercel Authentication, so team members must be signed in to Vercel to open them.

The workflow needs a repository secret named `VERCEL_TOKEN`. Without it the job does not fail — it emits a warning and skips the deploy.

```
# Create a token at https://vercel.com/account/tokens, then:
gh secret set VERCEL_TOKEN
```

The token is a long-lived account token, not the CLI login token. The CLI's own
credentials (`vca_`/refresh token under `%APPDATA%\com.vercel.cli`) expire and cannot
be reused here — Vercel refuses to mint new tokens from CLI auth.

#### Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Job fails with `VERCEL_TOKEN is invalid or expired` | Token revoked or past its expiry | Create a new token and re-run `gh secret set VERCEL_TOKEN` |
| Job warns `VERCEL_TOKEN is not configured` and skips | Secret missing (normal for forks) | Add the secret if this repo should deploy previews |
| Run sits in `queued` for hours and the REST API returns `Cannot cancel a workflow run that has not been queued yet` | GitHub-side queue stall on `push` events | Run the workflow from the Actions tab (`workflow_dispatch`); both workflows support it |

## Production Deployment

- The required production project for this repository is `traveling-ketch`.
- Before every Vercel deployment, run `vercel project ls` and `vercel inspect https://traveling-ketch.vercel.app` to confirm the target.
- Deploy only with `vercel --prod --yes` after the CLI reports this workspace is linked to `dolagobindamohanty/traveling-ketch`.
- Verify the deployed asset at `https://traveling-ketch.vercel.app/style.css` after production deployment.
- Do not deploy this repository to the separate `india-explorer` Vercel project unless the user explicitly asks for it.
