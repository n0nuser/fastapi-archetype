<a name="readme-top"></a>

# FastAPI Production Archetype

## Description

### Built With

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

Development:

* [Python 3](https://www.python.org/)
* [Poetry](https://python-poetry.org/)
* [FastAPI](https://fastapi.tiangolo.com/)
* [Pydantic](https://pydantic-docs.helpmanual.io/)
* [HTTPX](https://www.python-httpx.org/)

Development Tools:

* [Pre-Commit](https://pre-commit.com/)
* [Ruff](https://docs.astral.sh/ruff/)

Databases:

* [SQLAlchemy](https://www.sqlalchemy.org/)
* [PostgreSQL](https://www.postgresql.org/)

Deployment:

* [Uvicorn](https://www.uvicorn.org/)
* [Docker](https://www.docker.com/)
* [Docker-Compose](https://docs.docker.com/compose/)

Testing:

* [Pytest](https://docs.pytest.org/en/stable/)
* [Pytest-Mock](https://pytest-mock.readthedocs.io/en/latest/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

### Prerequisites

Install dependencies with Poetry.

> If you don't have Poetry: `pip install poetry`
> For documentation refer to [Poetry](https://python-poetry.org/docs/) or to a little guide we made [here](docs/poetry.md).

From the root project run: `poetry install`.

You can select the environment in your IDE of reference poiting to `.venv` on the root path, or run `poetry shell` to activate the environment.

## Roadmap

See the [open issues](https://github.com/axpecloud/modernapps-back-int-reservationmanager/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

If you have a suggestion that would make this better, please clone the repo and create a pull request. Select the template that most suits your suggestion.

1. Clone the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Check that you have installed pre-commit hooks with `pre-commit install`.
4. Check that your branch is up to date with `git pull origin develop` and merge if it's necessary with `git merge origin develop`.
5. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
6. Push to the Branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request to the `develop` branch

### Flow of Git Branching

* From Feature to Feature: squash and merge
* From Feature to Develop: squash and merge
* From Develop to Main: fast-forward merge

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Deployment

### Explanation of Docker-Compose Files

#### docker-compose.yml

This file is used to deploy the microservices on local. It uses the `Dockerfile` of each microservice to build the image and then deploys them along with a PostgreSQL database.

This should be used along the environment variables file `.env` which contains the database credentials and the `ENVIRONMENT` env variable set to `DEV`.

### Deploying the Microservices

1. Change directory into `docker` folder.
2. Build the images the docker-compose you prefer. e.g. `docker-compose up --build --remove-orphans`
3. Deploy! e.g. `docker-compose up -d`.

### Save Images and Upload to a server

If you want to deploy the microservices on a server without uploading the project, you will need to save the images and upload them to the server.

1. Build the images that will be deployed with `docker-compose --build`
2. `docker save` the image that is generated. e.g. `docker save myprojectname:latest | gzip > myprojectname.tar.gz`
   1. > This command only works in Linux or in WSL.
3. Upload the `tar.gz` files to the server and the `docker-compose.yml`.
4. `docker load` the images. e.g. `docker load -i myprojectname.tar.gz`
5. Run Docker-Compose to deploy. e.g.  `docker-compose up -d`

<p align="right">(<a href="#readme-top">back to top</a>)</p>
