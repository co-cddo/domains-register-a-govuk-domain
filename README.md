**The project is in initial stages**

**README file is in work-in-progress. It will be updated as the project progresses.**

## Application description

The application is a frontend client to apply for gov.uk domains.
Registrars can use the application to apply for a domain name.

The CDDO Domains team will take the decision to approve or reject the application.

It's built with Python and Django.

## Installation instructions

These instructions are for running the project locally on docker.

Steps to run the project locally on docker:

1. Clone the repository
2. Go to the project directory: domains-register-a-govuk-domain
3. Ensure docker is running on your machine
4. Run one of the following commands to run the application:

- Using gunicorn:
    ```bash
    make up
    ```
- Using the Django development server:
    ```bash
    make up-devserver
    ```

When the application is run:
- Any migrations are applied to the database.
- Static files collected.
- Seed data (see below) is also applied if it doesn't already exist.

## Usage instructions

The user-facing application is accessible via http://localhost:8010

Note: The application is in initial stages and the forms are at prototype/R&D stage. The pages on the application and logic within them are not yet representative of application.

The team can view and assess registration applications via the Django admin site. Each time the app is started, it will create a superuser and a 'reviewer' (staff) user if these do not already exist. The credentials are:

- admin, ilovedomains
- reviewer, ilovedomains

## Development instructions

This project uses Poetry for dependency management and packaging. To install Poetry, follow the instructions at https://python-poetry.org/

To install dependencies for local development ( e.g. when using IDE to make changes ) , use `poetry install`.

This repository is set up with [pre-commit](https://pre-commit.com/) for style and error checking before every commit.
You should install pre-commit, then run `pre-commit install` from within the project directory.

### Updating fixtures

Seed data is included for users, a single user group ('reviewer') and enough records to populate a single registration application.

If the models are changed it will be necessary to update the seed data. New seed data can be produced with:

```
python manage.py dumpdata request --indent 2
```

If the models change to the extent that the permissions for staff/reviewer users have to be changed (e.g. to provide visibility of a new model in the admin site) the it will be necessary to update the seed data. Log into the admin site as a superuser and change the permissions for the `reviewer` group as required.

Then copy and paste the output of the following command into the `reviewer_group.json` file, replacing the existing content:

```
python manage.py dumpdata auth.group --indent 2
```

If additional groups are added or other fundamental changes made which mean the default superuser/reviewer user records are changed, then paste the output of the following command into the `users.json` file, again replacing the existing content:

```
python manage.py dumpdata auth.user --indent 2
```

### Synthetic data

For local development, or user testing, it is recommended to use synthetic data instead of sensitive production data. There is a management command to do so:

``` bash
./manage.py create_sample_data
```

It can be run either in the application running locally without docker, or in a docker shell (`make shell`) if the local app is running in docker.

If the database to be populated is remote (like in a test account in RDS), then you'll need to connect to the database using the instructions found in the `domains-api` repository, in the tools directory.

Then you'll need to change the `DATABASE_URL` environment variable, either in your local shell, or in the `docker-compose.yml` file. The format will be something like:

``` bash
DATABASE_URL: postgresql://password@host:5433/registration
```

- `password` will be the database password, as found in the secrets manager
- `host` will be `localhost`, or `host.docker.internal` if running in docker.

Once this is set you can run the `create_sample_data` command above. Note that this is a destructive operation since it'll delete existing applications before adding new ones. The db users will be unchanged though.


### Clearing the database

While we're in the early stages of development it makes sense to delete existing migrations and create them afresh. To enable this, use the `make clear-db` command. Seed data will be re-applied when the application is restarted.

### Changing the admin site theme

The admin site is themed using the [django-admin-interface](https://pypi.org/project/django-admin-interface/) package. This is a temporary measure pending implementation of a proper design for the team-facing interface. The CSS values for the theme are loaded from JSON when the application is first brought up, either locally using the `init-local.sh` script or within one of the CodePipeline steps when deploying to AWS.

The `django-admin-interface` package, in turn, loads these CSS values into admin site page as inline styles. Inline styles are, in general, forbidden by our content security policy so it is necessary to add a hash for the inline stylesheet to settings.py (see below).

### Handling inline scripts and stlyes

By default the Content Security Policy (CSP) generated by the [django-csp](django-csp.readthedocs.io) package forbids inline styles and scripts. In some cases these are desirable (very small scripts) or necessary (when generated by other packages).

Inline scripts and styles can be allowed globally using the `unsafe-inline` directive but this reduces the benefit of the CSP. Instead, add a hash of the inline script or style to the `CSP_SCRIPT_SRC` or `CSP_STYLE_SRC` variable in `settings.py`. The hash can be obtained by loading the page in the browser and opening the developer tools console, which will include an error due to the CSP forbidding it from loading the script/style in question. It also gives the hash it was expecting.

CSP directives take the form of space-separated strings, enclosed in single quotes, within a containing pair of double quotes. E.g. -

`"'self' 'sha256-Yrk+0r8BB7VG8...' 'sha256-NrZCcfqaGMD3xHpM...'"`

If tinline scripts or styles are ever changed, the hash must be changed as well.

## Make commands

Following are some of the make commands:

`make build` - Build the docker images

`make collectstatic` - Collect the static files

`make makemigrations` - Create migrations which will be applied on each application start

`make up` - Run the application on docker

`make up-devserver` - Run the application on docker using the Django development server

`make shell` - Open a bash console within the running application container (you'll get an error if the service isn't running)

`make down` - Stop the application on docker

`make clear-db` - Delete the database volume


## Unit testing

There is a unit test suite that is run when pushing to github. It can also be run manually
with:

`poetry run ./manage.py test`

Some tests require clamav to run or will try to send email, so if you're working on something else you might want to run specific tests instead, with:

`ENVIRONMENT=local poetry run ./manage.py tests.test_admin_approval.ModelAdminTestCase.test_create_approval_works_0_approve`

## End-to-end testing

You need to have NodeJS installed, along with npm.

First, install cypress, the test framework:

```
npm install
```

Then, to run the tests, you need to have the prototype running on port 8000 (see above), then run:

```
npx cypress run
```

Note that the cookie banner tests require the application to run with the `GOOGLE_ANALYTICS_ID` environment variable set to something that starts with `GTM-`. The easiest way is to add `GOOGLE_ANALYTICS_ID=GTM-TEST` in your `.env` file.
