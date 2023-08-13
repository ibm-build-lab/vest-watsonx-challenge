#!/bin/bash

# start with generating static front-end assets
npm ci
npm run build --workspace=client

# checking registry var
[[ -z "${REGISTRY_HOSTNAME}" ]] && HOSTNAME='' || HOSTNAME="${REGISTRY_HOSTNAME}/"

# checking namespace var
[[ -z "${ICR_NAMESPACE}" ]] && NAMESPACE='' || NAMESPACE="${ICR_NAMESPACE}/"

# checking repo var
[[ -z "${DEPLOY_IMAGE_NAME}" ]] && IMAGE_NAME=$(npm run var:image-name -s) || IMAGE_NAME="${DEPLOY_IMAGE_NAME}"

# checking version var
[[ -z "${DEPLOY_IMAGE_VERSION}" ]] && IMAGE_VERSION=$(npm run var:image-version -s) || IMAGE_VERSION="${DEPLOY_IMAGE_VERSION}"

# build the actual docker image
docker build . --progress=plain --no-cache -t $HOSTNAME$NAMESPACE$IMAGE_NAME:$IMAGE_VERSION
