# CAMPUS Django Project - AI Agent Instructions

## Project Overview
CAMPUS is a Django-based community platform with modular apps for user accounts, discussion threads, media uploads, and planned features like forums, rankings, skill exchange, and lost & found.

## Essential Setup & Commands
- **Environment**: Always activate virtual environment (`source venv/bin/activate`)
- **Database**: Run `python manage.py migrate` after pulling changes
- **Development Server**: `python manage.py runserver`
- **Testing**: `python manage.py test` (note: test files are currently empty)
- **New Dependencies**: `pip install package-name && pip freeze > requirements.txt`

See [README.md](README.md) for complete setup instructions.

## Architecture & Conventions
- **App Structure**: Each feature in `apps/` with standard Django files (models.py, views.py, admin.py, etc.)
- **Custom User Model**: Email-based authentication in `accounts.User`
- **Soft Deletes**: Use `deleted_at` field instead of hard delete; always filter `deleted_at=None` in queries
- **Status Models**: Separate models for state management (ThreadStatus, etc.)
- **Admin Customization**: Use `@admin.register`, inlines, search/filter fields
- **URLs**: Include app URLs with namespaces

## Key Patterns & Pitfalls
- **Models**: Follow `threads` app for complex domains (self-referencing, voting, attachments)
- **Avoid**: Hard deletes; duplicate votes (unique constraints); stale denormalized counts
- **Migrations**: Create via `makemigrations` when changing models
- **Media**: User-organized upload paths (`uploads/user_{id}/`)
- **Incomplete Apps**: `forum`, `rankings`, etc. have placeholder code

## Key Files
- [campus/settings.py](campus/settings.py): INSTALLED_APPS, database config, custom User
- [apps/accounts/models.py](apps/accounts/models.py): Custom User & Profile models
- [apps/threads/models.py](apps/threads/models.py): Rich domain model example
- [apps/threads/admin.py](apps/threads/admin.py): Admin customization example

When working on new features, reference existing apps for patterns. Always run migrations and tests before committing.