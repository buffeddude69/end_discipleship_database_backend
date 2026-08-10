# Church Group Tracker — Backend

Django REST Framework API for tracking small groups, leadership groups,
and campus ministries: who leads them, who's in them, and whether
they're actively meeting.

## Project layout

```
config/       Django project settings, root urls
accounts/     Custom User model (group leaders) + auth endpoints
groups/       Group model (the small group / leadership group / campus ministry)
members/      Member model (people led within a group) + DiscipleshipStage lookup
```

## Setup

1. Create and activate a virtualenv, then install dependencies:
   ```
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in real values (at minimum, a
   Postgres database that already exists).
3. Run migrations and create a superuser:
   ```
   python manage.py migrate
   python manage.py createsuperuser
   ```
4. Run the dev server:
   ```
   python manage.py runserver
   ```

**Note:** `requirements.txt` includes a few production-only packages
(`django-storages`, `whitenoise`, `dj-database-url`, `gunicorn`) used for
deployment. `settings.py` is written so the app runs fine locally without
these installed at all -- they only activate when their related env vars
(`DATABASE_URL`, `SUPABASE_S3_ENDPOINT_URL`, etc.) are actually set. If you
want the leanest possible local setup, you can skip installing those five
and just install the "Core" section of `requirements.txt`.

## Media storage (profile pictures, remarks photos)

By default, uploaded photos save to a local `media/` folder -- fine for
local development. **For production, this won't survive a restart or
redeploy on most free hosting platforms**, since their disks are wiped
between deploys. To fix this, point uploads at Supabase Storage instead:

1. In your Supabase project, go to **Storage** and create a new bucket
   (e.g. `media`). Set it to **Public**, since the app displays these
   images directly by URL without a signed-request step.
2. Go to **Storage -> S3 Connection** and generate S3 access keys.
3. Set these environment variables (see `.env.example`):
   `SUPABASE_S3_ENDPOINT_URL`, `SUPABASE_S3_ACCESS_KEY_ID`,
   `SUPABASE_S3_SECRET_ACCESS_KEY`, `SUPABASE_S3_BUCKET_NAME`,
   `SUPABASE_S3_REGION`.

With those set, `settings.py` automatically switches file storage to
Supabase. Leave them unset locally and nothing changes.

## API endpoints (v1)

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register/` | Create a leader account |
| POST | `/api/auth/login/` | Get an auth token |
| GET/PATCH | `/api/auth/me/` | View/update your own profile |
| GET/POST | `/api/groups/` | List your groups / create a group |
| GET/PATCH/DELETE | `/api/groups/{id}/` | Manage one group |
| GET/POST | `/api/members/` | List/add members (scoped to your groups) |
| GET/PATCH/DELETE | `/api/members/{id}/` | Manage one member |
| GET | `/api/discipleship-stages/` | List configured discipleship stages |

Auth uses DRF Token Authentication: send `Authorization: Token <key>`
on every request after login/register.

Leaders only ever see and edit their own groups/members. Staff/admin
accounts (`is_staff=True`) can see everything — useful for a
church-wide coordinator role.

## Design notes / things we deliberately kept flexible

- **DiscipleshipStage is a table, not a hardcoded choice field.** Stage
  names/order are ministry-specific and will likely change — manage
  them from `/admin/` rather than a code deploy.
- **`Group.is_active` is a manual flag for now.** Once you have a few
  months of attendance data, this is the natural place to plug in
  automatic "inactive after N missed meetings" logic.
- **`Member.attendance_status` is a single current snapshot**, not a
  history log. If you'll want trends over time ("were they active in
  March?"), we should add a separate `AttendanceRecord` model
  (member, date, present/absent) later — happy to add this next once
  you confirm you want per-session history rather than just current
  status.
- **Year level / institution are free-text**, since school systems
  (grade school vs. college vs. postgrad) vary too much for a clean
  choice list.

## Next steps

1. Point `.env` at a real Postgres database and run `migrate`.
2. Seed a few `DiscipleshipStage` rows via `/admin/`.
3. Wire up the React frontend against these endpoints.
4. Decide if/when you want attendance *history* (see design notes above).
