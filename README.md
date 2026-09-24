# ENC Discipleship Database

A web app for a church organization to track small groups, leadership groups,
and campus ministries: who leads them, who's in them, and whether they're
actively meeting. Built as a Django REST Framework backend with a React +
TypeScript frontend.

This README documents the whole system as it stands today.

---

## 1. Tech Stack

**Backend**
- Django 6.x + Django REST Framework
- PostgreSQL (via Supabase in production, any local Postgres in dev)
- Token authentication (`rest_framework.authtoken`)
- Pillow (image uploads), django-storages + boto3 (S3-compatible media
  storage), whitenoise (static files), gunicorn (production server),
  dj-database-url (parses a single `DATABASE_URL`)

**Frontend**
- React 18 + TypeScript, built with Vite
- Tailwind CSS v4 (custom design tokens — see `src/index.css`)
- React Router
- No state-management library, no data-fetching library — plain
  `useState`/`useEffect` and a small hand-written `fetch` wrapper
  (`src/api/client.ts`). This was a deliberate choice to keep the app
  simple for a small team to maintain.

**Hosting**
- Frontend: Vercel
- Backend: Render (free web service)
- Database + file storage: Supabase (Postgres + S3-compatible Storage)

---

## 2. Project Structure

```
church_tracker/                  # Django backend
  accounts/                      # Leader accounts (custom User model)
  groups/                        # Groups (small group / leadership group / campus ministry)
  members/                       # Member/Intern profiles, GroupMembership, and lookup lists
  config/                        # settings.py, urls.py, wsgi.py
  manage.py
  requirements.txt

church-tracker-frontend/         # React frontend
  src/
    api/                         # types.ts, client.ts (fetch wrapper), labels.ts (display labels)
    components/                  # Shared form pieces, layout, route guards
    context/                     # AuthContext (login state)
    pages/                       # One file per screen
  vercel.json                    # SPA rewrite rule for Vercel
```

---

## 3. Data Model

### `accounts.User` (Leader accounts)
Extends Django's built-in user. This is the **only** representation of a
Leader in the system — see §5 for why there's no separate "Leader" profile
model.

| Field | Notes |
|---|---|
| `leader_role` | Small Group Leader / Leadership Group Leader / Campus Missionary |
| `demography` | High School / College / Single-Young Professional / Married / Parent / Senior |
| `gender`, `contact_number` | |
| `area` | Binan / Nuvali / Santa Rosa City — which area they disciple in |
| `year_level`, `school` (FK to `members.School`) | Only meaningful when `demography` is High School or College |
| `is_student` | **Not a real field** — a Python `@property` derived from `demography`. See §5. |
| `is_doing_one_on_one`, `one_on_one_with` | Simple optional checkbox + free-text "with whom" |

### `groups.Group`
| Field | Notes |
|---|---|
| `name`, `group_type` (Small Group / Leadership Group / Campus Ministry) | |
| `leader` | FK to `accounts.User` — the one person who owns/leads this group |
| `demography` | High School / College / Mixed / Others |
| `demography_other` | Required, validated, only when `demography = "others"` |
| `gender_composition`, `meeting_frequency`, `meeting_frequency_note`, `meeting_day`, `meeting_time`, `venue` | |
| `is_active` | Manually toggled for now (see §7, Known Trade-offs) |

### `members.Member` (shared Member/Intern profile)
**One profile per person, independent of any single group.** A person's
profile is created once and then linked to whichever group(s) they're
part of via `GroupMembership`. This was a deliberate restructure — see §5.

| Field | Notes |
|---|---|
| `first_name`, `last_name`, `gender` | Duplicate names (case-insensitive) are rejected at the API level |
| `role` | Member or Intern only — **not** Leader (see §5) |
| `year_level` | Elementary through 5th+ Year College, Out of School, or Adult |
| `school` | FK to `members.School` |
| `ministries` | Many-to-many with `Ministry` (a person can serve on more than one team) |
| `discipleship_stage` | FK to `DiscipleshipStage` |
| `remarks`, `remarks_photo` | Free text + optional photo upload |
| `is_doing_one_on_one`, `one_on_one_with` | Same simple checkbox pattern as on `User` |
| `updated_at` | Drives the "needs update" flag — see §6 |

### `members.GroupMembership` (the join between a person and a Group)
Links **either** a `Member` profile **or** a Leader `User` account to a
`Group` — never both, never neither. This is enforced two ways:
- A database `CheckConstraint` (`groupmembership_exactly_one_of_member_or_leader`)
- Serializer-level validation with a friendly error message

| Field | Notes |
|---|---|
| `group` | FK to `Group` |
| `member` | FK to `Member`, nullable |
| `leader` | FK to `accounts.User`, nullable |
| `attendance_status` | **New** (joined this month) / **Active** (attended this month) / **Inactive** |
| `status_updated_at` | Drives its own "needs update" flag, kept in sync with the Member's own timestamp — see §6 |

### Lookup tables (staff-managed under "Lists" in the app)
- `members.School` — `name`, `area` (free text), `demography` (free text). Seeded with an "Others" entry meant for Home Schooled / Elementary students.
- `members.Ministry` — just a `name`.
- `members.DiscipleshipStage` — `name` + `order` (controls display order).

---

## 4. Features

**Leader accounts**
- Staff-only account creation (no public self-registration — see §5)
- Profile fields: role, demography, gender, area, contact info, student
  status (derived), One2One status
- Self-service password change (rotates the auth token, so any old
  session/shared temp password stops working immediately)
- View any leader's profile (which groups they lead, which they're a
  member of)

**Groups**
- Create/edit/delete, assign a leader (staff can assign any leader;
  regular leaders are auto-assigned to themselves)
- Demography tagging (High School / College / Mixed / Others)
- Add existing Member/Intern profiles **or** existing Leader accounts to
  a group's roster, with monthly attendance status
- The "Add to Group" screen shows the full list of available people
  immediately (searchable), rather than requiring a search first

**Member/Intern profiles**
- One shared profile per person — searchable roster prevents duplicate
  profiles for the same person
- Full profile: school, year level, ministries (multi-select),
  discipleship stage, remarks + photo, One2One status
- Filters: by school, meeting day, "needs update this month," search by name

**Dashboard** (staff only)
- Total member profiles, total leader accounts, total group memberships
- Breakdown by role (Member/Intern), by this month's attendance status,
  by school, by area (both for students and for leaders)

**Admin/staff tools**
- "Lists" page: staff add/remove Schools, Ministries, and Discipleship
  Stages without touching Django admin
- Leaders directory with search

---

## 5. Key Design Decisions (and why)

**Member profiles are independent of Groups.**
Originally a `Member` had a direct FK to one `Group`. This was restructured
early on into the current `Member` + `GroupMembership` split specifically
so a leader adding someone to a group could search existing profiles
first, instead of accidentally creating a duplicate person every time
they show up in a different group.

**Leaders are never duplicated as Member profiles.**
There used to be a `role="leader"` option on `Member`, meant for people
in a leadership group. This was removed because it created two competing
records for the same real person — a Leader account *and* a Member
profile both describing them. `GroupMembership.leader` now lets a
leadership group's roster reference an actual Leader account directly.
A safe data migration reassigned any existing `role="leader"` profiles to
`"intern"` at the time (worth a one-time manual review if you inherited
old data from that period).

**`is_student` is a derived property, not a stored field.**
It was originally a separate checkbox alongside a `demography` field that
already distinguished High School/College — which was redundant and could
disagree with itself. It's now computed from `demography`, so there's
exactly one source of truth.

**School `area`/`demography` are free text, not dropdowns.**
These started as constrained choice fields (mirroring the org's 3 areas
and 4 demography categories), but were changed to plain text fields on
request, since schools don't always cleanly fit the org's own leader-area
categories. The "Others + explain" pattern was removed at the same time
since free text made it redundant.

**Registration is staff-only.**
This is an internal organizational tool, not a public product — open
self-signup wasn't appropriate. Staff create leader accounts (with a
temporary password) via a dedicated "Add Leader" flow that does **not**
reuse the login flow, specifically so creating someone else's account
doesn't log the staff member out of their own session.

**One2One tracking is intentionally simple.**
Originally designed with a "must specify who" requirement, this was
simplified to a plain optional checkbox + optional name field per
explicit request — no validation forcing a name.

---

## 6. The "Needs Update" Sync Fix

There are two independent "last updated" timestamps in the system: the
`Member` profile itself, and each `GroupMembership`'s attendance status.
Editing someone's attendance status from a Group page used to only touch
the `GroupMembership` record — the Member profile's own timestamp (which
the Members list checks) never moved, so the two "needs update" indicators
could disagree.

**Fix:** updating or creating a `GroupMembership` now also touches the
linked `Member`'s `updated_at`, since reviewing someone's attendance is a
meaningful check-in on them regardless of which screen you did it from.

**To test this without waiting a month:** in Supabase's Table Editor,
manually backdate a test member's `updated_at` in `members_member` to
last month, confirm the Members list shows "Needs update," then update
their attendance status from their group and confirm the flag clears.

---

## 7. Known Trade-offs / Backlog

- `Group.is_active` is still a manual toggle, not auto-derived from
  attendance trends.
- No pagination anywhere yet (fine at current scale; revisit if member
  lists grow large).
- `Member.remarks_photo` supports one photo, not multiple.
- No audit trail beyond the single `updated_at` timestamp per record —
  no history of *who* changed *what*.
- The dashboard is view-only; no export (CSV/PDF) yet.

---

## 8. Local Development

### Backend
```bash
cd church_tracker
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # fill in local Postgres credentials
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Only the "Core" packages at the top of `requirements.txt` (Django, DRF,
psycopg2-binary, django-cors-headers, Pillow) are needed for local dev.
The production-only packages (django-storages, boto3, gunicorn,
whitenoise, dj-database-url) are never imported unless their related
environment variable is actually set — see `config/settings.py`.

### Frontend
```bash
cd church-tracker-frontend
npm install
npm run dev
```

By default it talks to `http://127.0.0.1:8000`. Set `VITE_API_BASE_URL`
in a `.env` file to point elsewhere.

---

## 9. Deployment

**Database + Storage — Supabase**
1. Create a project, get the **Session pooler** connection string (not
   the direct `db.xxx.supabase.co` one — that only supports IPv6, which
   Render can't reach; the pooler is free and IPv4-compatible).
2. **Security:** Supabase auto-exposes every `public` schema table via
   its own REST API, separate from however your own backend connects.
   Since this app never uses that API, Row Level Security should be
   enabled (with zero policies) on every table to close it off — see
   `enable_rls_all_tables.sql` if you still have it, or re-run Supabase's
   Security Advisor and enable RLS on anything it flags. This does not
   affect Django's own access, since it connects as the table owner
   (which bypasses RLS by default).
3. (Optional) For photo uploads to persist across deploys, create a
   **public** Storage bucket and generate S3 keys under
   Storage → S3 Connection.

**Backend — Render**
- Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- Start command: `gunicorn config.wsgi`
- Environment variables needed: `DATABASE_URL` (the pooler string),
  `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS` (bare domain, no
  `https://` or trailing slash), `EXTRA_CORS_ORIGINS` (your Vercel
  domain), and optionally the five `SUPABASE_S3_*` vars for photo
  storage.
- Since Render's free tier has no Shell access, an idempotent
  `python manage.py ensure_superuser` management command creates an
  admin account from `DJANGO_SUPERUSER_USERNAME`/`DJANGO_SUPERUSER_PASSWORD`
  env vars — safe to include in the build command on every deploy.

**Frontend — Vercel**
- Set **Root Directory** to `church-tracker-frontend` if it's in a
  monorepo alongside the backend.
- Set `VITE_API_BASE_URL` to your Render backend's URL.
- `vercel.json` includes a rewrite rule so client-side routes
  (React Router) don't 404 on direct load or refresh.

---

## 10. Troubleshooting Reference

A few issues came up more than once during development — noting them
here in case they recur:

- **`ModuleNotFoundError` locally after a backend update:** a new
  package was added to `requirements.txt` — run `pip install -r
  requirements.txt` (or just the specific package) again.
- **Frontend build fails referencing a page/function that "should be
  deleted":** zip/file-copy updates only overwrite files that exist in
  both the old and new version — they never delete files that were
  removed. When replacing the frontend or backend wholesale, delete the
  old folder first rather than copying on top of it.
- **Django migration conflicts ("relation already exists") after
  restoring/recreating a database:** almost always leftover old
  migration files sitting alongside new ones for the same reason as
  above — the `migrations/` folder should only ever contain the exact
  set of files from the latest delivered version.
- **`django.db.utils.OperationalError` / "Network is unreachable"
  connecting to Supabase:** using the direct connection string instead
  of the Session pooler (see §9).
- **400 Bad Request on every page in production:** `ALLOWED_HOSTS` was
  set to a full URL (with `https://` and/or a trailing slash) instead of
  a bare hostname.
- **Vercel 404 on the root page:** Root Directory not set to the
  frontend's subfolder in a monorepo.
- **Vercel 404 on any page other than the root:** missing SPA rewrite
  rule (`vercel.json`).

---

## 11. API Overview

All endpoints are under `/api/`. Auth is via `Authorization: Token <key>`
header, obtained from `/api/auth/login/`.

| Endpoint | Notes |
|---|---|
| `POST /api/auth/login/` | Returns `{token, user}` |
| `POST /api/auth/register/` | **Staff only** — creates a leader account |
| `GET/PATCH /api/auth/me/` | Own profile |
| `POST /api/auth/change-password/` | Rotates the auth token on success |
| `GET /api/auth/leaders/`, `/api/auth/leaders/<id>/` | Any authenticated user can read |
| `/api/groups/` | Full CRUD, scoped to the leader's own groups (staff see all) |
| `/api/members/` | Full CRUD on shared profiles, visible to all authenticated leaders |
| `/api/group-memberships/` | Links a Member or Leader to a Group |
| `/api/schools/`, `/api/ministries/`, `/api/discipleship-stages/` | Read: anyone (schools are even public, unauthenticated, so the registration form can show them); Write: staff only |
| `/api/dashboard/` | Staff only |

---