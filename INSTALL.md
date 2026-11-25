# realityuncompiled README kit

## Contents
- `README.md` — profile README.
- `assets/profile-scene.jpg` — the image supplied in this conversation.
- `assets/contribution-maze.svg` — placeholder until the workflow runs.
- `scripts/generate_maze.py` — GitHub GraphQL contribution-calendar renderer.
- `.github/workflows/update-maze.yml` — daily scheduled update.

## Install
Copy all files and folders into the root of the `realityuncompiled` profile repository.
The repository name must match the GitHub username.

The workflow currently assumes the default branch is `main`. Change the branch name
in the workflow if your default branch differs.

## Enable write access
Repository Settings → Actions → General → Workflow permissions →
**Read and write permissions**.

The workflow uses the automatic `GITHUB_TOKEN`. No personal access token is normally
needed. If your account or organization policy prevents the query, use a suitable
token as a repository secret named `GH_TOKEN` and update the workflow accordingly.

## Run locally
Python 3.10+; no third-party packages:

```bash
GITHUB_USERNAME=realityuncompiled GH_TOKEN=YOUR_TOKEN python scripts/generate_maze.py
```

PowerShell:

```powershell
$env:GITHUB_USERNAME = "realityuncompiled"
$env:GH_TOKEN = "YOUR_TOKEN"
python scripts/generate_maze.py
```

## Styling limitations
GitHub README files do not support arbitrary CSS or JavaScript. Styling is implemented
through SVG artwork and supported Markdown/limited HTML. The scene image acts as a
wide visual header, not a true page background. The cat is static by design.

The maze is based on the GitHub contribution calendar. It is a visual metaphor, not
a navigable game or a measure of skill. Quiet days are part of the map, too.
