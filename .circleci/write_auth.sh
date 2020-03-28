#!/bin/bash

AUTH_PATH=/home/circleci/project/tests/resources/secrets.json

echo "{" > ${AUTH_PATH}
echo "  \"email\": \"${OVERLEAF_EMAIL}\"," >> ${AUTH_PATH}
echo "  \"password\": \"${OVERLEAF_PASSWORD}\"," >> ${AUTH_PATH}
echo "  \"git_url\": \"${OVERLEAF_URL}\"," >> ${AUTH_PATH}
echo "}" >> ${AUTH_PATH}
