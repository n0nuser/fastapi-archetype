# Deployment

This section contains the deployment instructions for the microservices.

The microservice should be working in the deployment if the `src` folder contains the project, and the `app.py` file isn't modified too much.

You can change those files to fit your project, but take in account the Docker files might need to be modified.

## Docker

The microservices are deployed using Docker. The `Dockerfile` is used to build the image ([reference](https://docs.docker.com/get-started/overview/#images)) and then deploy it.

### Docker-Compose

This file is used to deploy the microservices. It uses the `Dockerfile` to build the image and then deploys it along with a PostgreSQL database.

This should be used along the environment variables file `.env` which contains the environment variables for the microservices.

## Deploying the Microservices

1. Change directory into `docker` folder.
2. Build the images. e.g. `docker-compose up --build --remove-orphans`
3. Deploy! e.g. `docker-compose up -d`.

Take in account an `.dockerignore` file could exist to avoid copying unnecessary files to the image.

### Save Images and Upload to a server

If you want to deploy the microservices on a server without uploading the project, you will need to save the images and upload them to the server.

1. Build the images that will be deployed with `docker-compose --build`
2. `docker save` the image that is generated. e.g. `docker save myprojectname:latest | gzip > myprojectname.tar.gz`
   1. > This command only works in Linux or in WSL.
3. Upload the `tar.gz` files to the server and the `docker-compose.yml`.
4. `docker load` the images. e.g. `docker load -i myprojectname.tar.gz`
5. Run Docker-Compose to deploy. e.g.  `docker-compose up -d`

<p align="right">(<a href="#readme-top">back to top</a>)</p>
