# Publishing to GitHub and Streamlit

## Option A: no command line
1. On github.com choose **New repository**. Name it `uwazi-trace`, make it **Public**, and do not tick "Add a README".
2. Click **uploading an existing file**, then drag in everything from the unzipped folder, including the hidden `.streamlit` and `.github` folders.
   (If your computer hides them, turn on "show hidden files" first.)
3. Commit the upload.
4. Edit `README.md` on GitHub: replace `YOUR-USERNAME` and `YOUR NAME`.

## Option B: command line
```bash
python scripts/set_username.py Rene12-3 "Your Name"
git init -b main
git add .
git commit -m "Initial commit: Uwazi Trace prototype"
git remote add origin https://github.com/Rene12-3/uwazi-trace.git
git push -u origin main
```
Create the empty repository on GitHub first. After the first push, the CI badge in the README turns green once the workflow passes.

## Public demo on Streamlit Community Cloud
1. Sign in at https://share.streamlit.io with GitHub.
2. **Create app**, choose the repository, branch `main`, main file `streamlit_app.py`.
3. Optional: in Advanced settings add `FEEDBACK_URL` (a form or `mailto:` link).
4. Deploy. You get a link like `https://your-name-uwazi-trace.streamlit.app`.

Free apps sleep after inactivity and wake on the next visit. Never deploy this prototype with real or sensitive data.

## Repository settings worth switching on
- Description and topics (for example `public-procurement`, `transparency`, `kenya`, `open-data`)
- Branch protection on `main` (require the CI check)
- Private vulnerability reporting (Security tab)
- Add `docs/screenshots/01-today.png` as the social preview image
