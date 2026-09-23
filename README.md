# ENC Discipleship Database — Backend

## Overview

This repository contains the backend API for a **ENC Discipleship Database** built with Django and Django REST Framework.

The system is designed to help church staff and group leaders manage church groups and their members. The backend handles user authentication, group management, member profiles, and role-based access control.

The application has two primary user roles:

* **Staff** — Administrative users who can manage user accounts, groups, and member profiles.
* **Group Leaders** — Users who manage the groups they are assigned to and the members associated with those groups.

Because the system is intended for private use, Group Leader accounts cannot be freely registered. User accounts are created by Staff members.

The backend provides a REST API consumed by the separate React TypeScript frontend.

---

## Features

* User authentication using authentication tokens
* Role-based permissions for Staff and Group Leaders
* Staff account management
* Group creation and management
* Member profile management
* Assignment of members to groups
* Support for members belonging to multiple groups
* Group Leader assignment and management
* Django administration interface

---

## Tech Stack

* **Python**
* **Django**
* **Django REST Framework**
* **PostgreSQL** — database
* **Token Authentication** — API authentication
* **React + TypeScript** — frontend client
* **Supabase** - Database hosting and deployment
* **Render** - backend hosting and deployment

---

## User Roles and Permissions

### Staff

Staff members have administrative access to the system.

They can:

* Create and manage Group Leader accounts
* Manage groups
* Manage member profiles
* Oversee the groups and their members
* Perform administrative operations across the system

### Group Leaders

Group Leaders are user accounts created by Staff.

They can:

* Access groups they are assigned to
* Manage information related to their assigned groups
* Create and manage member profiles within their groups
* Be associated with a group as a member

Group Leaders should not be able to modify groups that they are not responsible for.

---

## Data Relationships

The system manages three primary concepts: **Users, Groups, and Members**.

A simplified relationship can be represented as:

```text
                    User
                     │
              ┌──────┴──────┐
              │             │
            Staff       Group Leader
                              │
                              ▼
                           Groups
                              │
                       ┌──────┴──────┐
                       │             │
                    Leaders       Members
                                     │
                                     │
                            Multiple Groups
```

A member can belong to **multiple groups**, allowing the same member profile to be associated with different church groups.

---

## Authentication

The backend uses token-based authentication for API access.

The general authentication flow is:

```text
User Login
    │
    ▼
Django REST API
    │
    ▼
Authentication
    │
    ▼
Authentication Token
    │
    ▼
Authenticated API Requests
```

Users include their authentication token when making requests to protected API endpoints.

Since this is a private system, account creation is restricted to Staff users rather than allowing public registration.

---

## Prerequisites

Before running the backend locally, install the following:

* Python
* PostgreSQL
* Git

You may also need:

* A code editor such as Visual Studio Code
* A PostgreSQL client such as pgAdmin

---

## Installation

### 1. Clone the Repository

```bash
git clone <BACKEND_REPOSITORY_URL>
cd <BACKEND_DIRECTORY>
```

### 2. Create a Virtual Environment

Windows:

```powershell
python -m venv .venv
```

Activate the virtual environment:

```powershell
.venv\Scripts\activate
```

For macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Database Setup

After configuring the database, apply Django migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

If the project requires a Django superuser for administration:

```bash
python manage.py createsuperuser
```

Follow the prompts to create the administrator account.

---

## Running the Development Server

Start the Django development server with:

```bash
python manage.py runserver
```

The backend will normally be available at:

```text
http://127.0.0.1:8000/
```

The exact host and port may be changed depending on the project's configuration.

---

## API

The backend exposes REST API endpoints used by the frontend application.

The API is responsible for operations involving:

* Authentication
* Users
* Groups
* Members
* Group memberships
* Administrative operations

### Responsibilities

**URLs** determine which view handles an incoming request.

**Views** process the request and determine the appropriate response.

**Permissions** determine whether the authenticated user is allowed to perform the requested operation.

**Serializers** validate incoming data and convert Django model data into JSON responses.

**Models** define the application's data structure and relationships with the database.

---

## Django Admin

The Django admin interface provides an administrative interface for managing backend data.

After creating a superuser, run the development server and access:

```text
http://127.0.0.1:8000/admin/
```

---

## Testing

The backend contains automated tests for verifying application behavior.

Run the Django test suite with:

```bash
python manage.py test
```

Tests can be used to verify functionality such as:

* Authentication
* Permissions
* Group operations
* Member operations
* API responses
* Validation
* Access restrictions

---

## Frontend Integration

The backend is designed to work with a separate **React TypeScript frontend**.

The general architecture is:

```text
┌──────────────────────┐
│ React + TypeScript   │
│      Frontend        │
└──────────┬───────────┘
           │
           │ REST API
           ▼
┌──────────────────────┐
│ Django REST          │
│ Framework Backend    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│     PostgreSQL       │
└──────────────────────┘
```

The frontend communicates with the backend through HTTP requests and receives JSON responses from the REST API.

The frontend repository can be found here:

```text
<FRONTEND_REPOSITORY_URL>
```

---

## Security Considerations

The application uses authentication and permissions to restrict access to protected resources.

In particular:

* User accounts are not publicly registered.
* Staff members are responsible for creating Group Leader accounts.
* Protected API endpoints require authentication.
* Permissions determine which operations users can perform.
* Group Leaders should only be able to modify groups they are assigned to.
* Sensitive environment variables should not be committed to the repository.

---

## Development

When making changes to the backend, remember to create and apply migrations when modifying Django models:

```bash
python manage.py makemigrations
python manage.py migrate
```

Run the test suite before committing changes:

```bash
python manage.py test
```

---

## Related Repository

### Frontend

The frontend application is maintained in a separate repository and is built with React and TypeScript.

```text
<FRONTEND_REPOSITORY_URL>
```

---

