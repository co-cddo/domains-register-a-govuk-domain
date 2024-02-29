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
4. Run the following command to run the application:
```bash
make collectstatic; make up
```

The command `make collectstatic` is to collect the static files and `make up` is to run the application on docker.

`make collectstatic` is a one-time command to collect the static files. It is not required to run this command every
time, unless there are changes in the static files.

So after the first time, the command to run the application on local docker is:
```bash
make up
```

## Usage instructions

The application will be accessible via http://localhost:8000/name

Note: The application is in initial stages and the forms are at prototype/R&D stage. The pages on the application and
logic within them are not yet representative of application.

## Development instructions

This project uses Poetry for dependency management and packaging. To install Poetry, follow the instructions at
https://python-poetry.org/

To install dependencies for local development ( e.g. when using IDE to make changes ) , use `poetry install`.

## Make commands

Following are some of the make commands:

`make build` - Build the docker images

`make collectstatic` - Collect the static files

`make up` - Run the application on docker

`make down` - Stop the application on docker


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
