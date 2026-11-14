# DevOps and contribution flow

## Repository layout

- Integrated/backend repository: `ivanbright/rodai-backend` (the root workspace and deployment build context).
- Frontend repository: `ivanbright/rodai-frontend`, included by the integrated repository as a Git submodule at `frontend/`.
- The frontend commit is pushed separately; update the submodule pointer in the backend repository when consuming a frontend change. This keeps the production build reproducible while preserving separate histories.

## Branch and merge flow

1. Keep `main` as the integration branch.
2. Create a short-lived branch for each focused change.
3. Push the branch and open a pull request into `main`.
4. Require the corresponding GitHub Actions checks before merging: backend lint/tests and integrated Docker build; frontend lint/tests/build in its repository.
5. Use squash or merge commits consistently (owner to select repository policy). Do not force-push shared branches.
6. After each approved project phase, create the required `rodai-phase-N` tag only after its acceptance criteria pass.

## GitHub repository settings still to enable

Workflow YAML cannot itself enforce a merge gate. In each repository, set the default branch to `main`, protect `main` (or add a ruleset), require pull requests, require the passing workflow status checks, block force pushes and deletion, and require branches to be up to date if the owner wants strict gating. Restrict bypasses to repository administrators. These settings have not been applied because repository administration access is not available in this workspace.

## CI behavior

- CI runs on pull requests targeting `main`, pushes to `main`, and manual dispatch.
- Jobs use read-only repository permissions, cancel obsolete runs on the same ref, and never deploy or publish artifacts.
- Backend CI lints/tests and builds the integrated image with its frontend submodule.
- Frontend CI uses `npm ci`, lint, tests, and production build.
- Dependabot checks GitHub Actions and language dependencies monthly. Review and merge its update PRs only after checks pass.
- Deployment automation, secrets, production migrations, and Railway release promotion are deliberately separate future work; Phase 1B requires owner deployment settings and credentials.

## Current blockers

The frontend lockfile is now committed and Docker Compose builds and runs locally. No workflow has run on GitHub, and branch protection is not configured; do not treat YAML workflows as an exercised merge gate until an Actions run succeeds and required checks are enabled. The latest `npm ci` reported 14 dependency vulnerabilities; the npm audit endpoint could not be reached because TLS certificate verification failed, so advisory details need follow-up before deployment.
