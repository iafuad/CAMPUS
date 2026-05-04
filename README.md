CAMPUS — Development Setup
==========================

This guide explains how to set up the project for local development.

**Prerequisites**
- **Python:** 3.8+ recommended. Verify with `python3 --version`.
- **pip:** Python package installer.
- (Optional) **git:** to clone the repository.

**Create a virtual environment**
1. From the project root, create a venv named `venv` (recommended):

```bash
python3 -m venv venv
```

2. Activate the virtual environment:

```bash
# Linux / macOS
source venv/bin/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

3. Upgrade pip and install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

If your environment uses pinned versions, you may also consult `requirements_versions.txt`.

**Environment variables**
- The project may read environment variables for secret keys, database settings, etc. Create a `.env` file or set variables in your shell. Example variables you might need:

```
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=postgres://user:pass@localhost:5432/dbname
```

Add any project-specific variables described by the maintainers.

**Database setup & migrations**
1. If you changed models, create migrations locally (only when developing models):

```bash
python manage.py makemigrations
```

2. Apply migrations to create/update the database schema:

```bash
python manage.py migrate
```

3. Create a superuser to access the admin interface:

```bash
python manage.py createsuperuser
```

**Static files**
During development Django serves static files automatically. If you need to collect static files (for production-like workflows):

```bash
python manage.py collectstatic --noinput
```

**Run the development server**
Start the local server on the default port 8000:

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

**Run tests**
Run the Django test suite:

```bash
python manage.py test
```

**Common tasks**
- Install a new package: `pip install package-name` then update `requirements.txt`:

```bash
pip freeze > requirements.txt
```

- Linting / formatting: add and run tools as needed (e.g., `flake8`, `black`).

**Notes for contributors**
- Follow the existing project structure under the `apps/` folder. Each app contains its own models, views and migrations.
- Keep `requirements.txt` up-to-date when adding packages.
- Run migrations and tests locally before opening pull requests.

If you want, I can add a `.env.example` file, a contributor checklist, or Docker/devcontainer configs—tell me which you'd prefer.

