# A generic API container for running Azure ML model workloads
#
# Description: This dockerfile builds an generic API container image.  The API is an Python application and exposes an
# endpoint for serving Azure ML models and predicting outcomes.
#
# NOTES:
#
#
FROM continuumio/miniconda3
MAINTAINER Ganesh Radhakrishnan ganrad01@gmail.com

WORKDIR /app

# Update OS and install gcc
RUN apt-get update
# 'cc1' library is required to compile pre-processed C files into assembly code!
RUN apt-get -y install --reinstall build-essential
RUN apt-get -y install gcc

# Create the environment:
COPY project_env.yml .
RUN conda env create -f project_env.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "project_environment", "/bin/bash", "-c"]

# Copy all the application files to /app
COPY . .

# Expose flask default listen port (5000)
EXPOSE 5000

# Run the application when container is started
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "project_environment", "python", "main-generic.py"]
