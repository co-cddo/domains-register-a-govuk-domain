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

The user-facing application is accessible via http://localhost:8000

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

### Clearing the database

While we're in the early stages of development it makes sense to delete existing migrations and create them afresh. To enable this, use the `make clear-db` command. Seed data will be re-applied when the application is restarted.

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
