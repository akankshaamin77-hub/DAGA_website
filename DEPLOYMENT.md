# DAGA deployment notes

GitHub Pages hosts only the HTML/CSS/JavaScript frontend. It does not execute Flask
or host MySQL. Deploy the backend and database separately.

## Backend deployment
Deploy this folder as a Python web service (for example, Render).
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Configure environment variables: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`,
  and `DB_NAME` (normally `daga_db`).
- Create the MySQL database and run all six `daga_database_*.sql` files.
- Open the backend root URL; it should return JSON confirming the backend is running.

## Frontend deployment
1. Edit `config.js`.
2. Replace `https://YOUR-BACKEND-SERVICE.onrender.com` with the real deployed API URL,
   without a trailing slash.
3. Push all files to the repository root.
4. In GitHub repository Settings -> Pages, choose Deploy from a branch, `main`, `/ (root)`.

## Corrections included
- Centralized API URL; removed hard-coded loopback API URLs from JavaScript.
- Fixed signup redirect to `index.html`; this ZIP contains no `login.html`.
- Removed stray top-level admin dashboard code referencing out-of-scope variables.
- Configured Flask to bind to `0.0.0.0` and the hosting platform's `PORT`.
- Configured MySQL connection via environment variables.
- Added Gunicorn to requirements.

## Security note
The existing app uses localStorage/sessionStorage for client-side login state.
That is not secure authorization. Before public launch, implement server-side sessions
or token validation and protect admin/business endpoints. Never commit real DB secrets.
