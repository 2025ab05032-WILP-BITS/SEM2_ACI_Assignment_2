Package README
================

This package helper creates a zip archive of the repository contents (excluding `.git`) that you can upload or extract locally and push as a new branch.

How to create the package (Windows PowerShell):

```powershell
cd "d:\BITS\SEM-2\ACI\Assignment-2\SEM2_ACI_Assignment_2-main\SEM2_ACI_Assignment_2-main"
# run the included script
.\\create_package.ps1
# the script will produce improve-minimax-readme-tests.zip in the same folder
```

How to use the package to create a branch and push to GitHub (local steps):

1. On your machine, unzip the archive to a temporary folder.
2. Initialize a new git repo or copy files into an existing clone.

Option A — push as a new branch from a fresh clone:

```powershell
# from a local clone of your GitHub repo
cd path\to\local\clone
# create and switch to a new branch
git checkout -b improve/minimax-readme-tests
# copy files from the unzipped package into the repo (overwrite as needed)
robocopy /MIR "C:\path\to\unzip\folder" "." 
# stage and commit
git add .
git commit -m "Improve Minimax: MRV heuristic, consistent exceptions; update README, tests, add diagnostics"
# push branch
git push -u origin improve/minimax-readme-tests
```

Option B — create a branch directly inside the unzipped package and push (if you have network/auth set up):

```powershell
cd C:\path\to\unzip\folder
git init
git remote add origin https://github.com/2025ab05032-WILP-BITS/SEM2_ACI_Assignment_2.git
git checkout -b improve/minimax-readme-tests
git add .
git commit -m "Improve Minimax: MRV heuristic, consistent exceptions; update README, tests, add diagnostics"
git push -u origin improve/minimax-readme-tests
```

Notes:
- If `git push` requires authentication, use your GitHub credentials or a Personal Access Token (PAT) when prompted, or set up SSH keys.
- The packaging script excludes `.git` to avoid committing repository metadata; use Option A if you prefer to merge into an existing clone.

If you want, I can attempt the push from this environment (I tried earlier but a lingering Python process blocked the terminal). If you prefer, run the script locally and push the produced branch; paste any errors here and I'll help fix them.