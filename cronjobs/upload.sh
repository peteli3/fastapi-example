#!/bin/sh

if [ $# -ne 3 ]; then
    echo "Usage: $0 <bucket_name> <region> <file_path>" >&2
    exit 1
fi

BUCKET_NAME=$1
REGION=$2
FILE_PATH=$3

if [ -z $BUCKET_NAME ] || [ -z $REGION ] || [ -z $FILE_PATH ]; then
    echo "Error: Bucket name, region, and file path must be provided." >&2
    exit 1
fi

if [ -z "${ACCESS_KEY}" ] || [ -z "${SECRET_KEY}" ]; then
    echo "Error: ACCESS_KEY or SECRET_KEY not set or empty." >&2
    exit 1
fi

# TODO validate file
# TODO upload file to linode object storage

echo "Uploaded $(basename $FILE_PATH) to ${BUCKET_NAME}.${REGION}.linodeobjects.com"
