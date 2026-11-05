# Workspace Guidance

## Production Deployment

- The required production project for this repository is `traveling-ketch`.
- Before every Vercel deployment, run `vercel project ls` and `vercel inspect https://traveling-ketch.vercel.app` to confirm the target.
- Deploy only with `vercel --prod --yes` after the CLI reports this workspace is linked to `dolagobindamohanty/traveling-ketch`.
- Verify the deployed asset at `https://traveling-ketch.vercel.app/style.css` after production deployment.
- Do not deploy this repository to the separate `india-explorer` Vercel project unless the user explicitly asks for it.
