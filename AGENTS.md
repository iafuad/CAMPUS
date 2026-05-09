# CAMPUS Django Project - AI Agent Instructions

## Project Overview
CAMPUS is a Django-based community platform with modular apps for user accounts, discussion threads, media uploads, and planned features like forums, rankings, skill exchange, and lost & found.

**App Status:**
- **Active**: accounts, threads, media, academics
- **Partial**: lost_found (models only), skill_exchange (models only)
- **Placeholder**: forum (model only), rankings (skeleton)

## Essential Setup & Commands
- **Environment**: Always activate virtual environment (`source venv/bin/activate`)
- **Database**: Run `python manage.py makemigrations` after making any model changes
- **Development Server**: `python manage.py runserver`
- **Testing**: Proper testing method is not implemented yet. Use `python manage.py check` for checking potential errors for now
- **New Dependencies**: Run `pip freeze > requirements_versions.txt` after installing new dependencies
- **Static Files**: `python manage.py collectstatic --noinput` for production-like setup

See [README.md](README.md) for complete setup instructions.

## Architecture & Conventions
- **App Structure**: Each feature in `apps/` with standard Django files (models.py, views.py, admin.py, etc.)
- **Custom User Model**: Email-based authentication in `accounts.User`; handle as unique identifier
- **Soft Deletes**: Use `deleted_at` (DateTimeField, nullable) or `is_deleted` (boolean)
- **Status Models**: Separate TextChoices enums in [apps/common/choices.py](apps/common/choices.py) (40+ choice classes)
- **Signals**: Use for OneToOne creation (e.g., UserProfile via [apps/accounts/signals.py](apps/accounts/signals.py))
- **Admin Customization**: Use `@admin.register`, inlines, search/filter fields; reference [apps/threads/admin.py](apps/threads/admin.py)
- **URLs**: Include app URLs with namespaces

## Key Patterns & Pitfalls
- **Models**: Follow `threads` app for complex domains (self-referencing, voting, attachments); use unique constraints to prevent duplicates
- **Avoid**: Hard deletes; stale denormalized counts (use aggregation instead); incomplete apps without migrations
- **Migrations**: Create via `makemigrations` when changing models; check pending for partial apps (skill_exchange, lost_found)
- **Media**: User-organized upload paths (`uploads/user_{id}/`); soft delete via boolean flag
- **Incomplete Apps**: forum (model wraps threads, no views), rankings (XP skeleton), skill_exchange (rich models, no views), lost_found (models, no admin/views)
- **Denormalized Counts**: Update manually (e.g., vote counts); prefer database aggregation for accuracy

## Key Files
- [campus/settings.py](campus/settings.py): INSTALLED_APPS, database config, custom User, media/static paths
- [apps/accounts/models.py](apps/accounts/models.py): Custom User & Profile models, UserManager
- [apps/accounts/signals.py](apps/accounts/signals.py): UserProfile creation signal
- [apps/common/choices.py](apps/common/choices.py): All TextChoices enums for domain values
- [apps/threads/models.py](apps/threads/models.py): Rich domain model example (Thread, Message, Vote, Attachment)
- [apps/threads/admin.py](apps/threads/admin.py): Admin customization example with inlines

When working on new features, reference existing apps for patterns.

## Agent Guidelines for AI coding agents

- **First steps:** Activate the virtualenv (`source venv/bin/activate`), run `python manage.py check` and `python manage.py runserver` to reproduce runtime issues locally.
- **Safe workflow:** 1) Read related files in `apps/<name>/` (models, views, admin).
- **Design expectations:** Use the `accounts` and `threads` apps as canonical patterns for models, signals, admin, and uploads. Prefer soft deletes (`deleted_at`/`is_deleted`) over hard deletes and avoid denormalized counts unless updating aggregation logic.
- **Conventions to follow:** Email-based `User` as primary identifier, TextChoices in [apps/common/choices.py](apps/common/choices.py), media uploads under `media/uploads/user_{id}/`.
- **When adding features:** Include admin registration where appropriate, and link new documentation in this file rather than duplicating long docs.
- **Where to look first:** [campus/settings.py](campus/settings.py), [apps/accounts/models.py](apps/accounts/models.py), [apps/threads/models.py](apps/threads/models.py), [apps/common/choices.py](apps/common/choices.py).