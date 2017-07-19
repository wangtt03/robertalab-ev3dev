#!/bin/bash

ROBERTADIR=$(dirname "$0")
cd ${ROBERTADIR}
ROBERTADIR=$(pwd)

build_dir=$ROBERTADIR
output_dir=$ROBERTADIR/$1
if [ -d "$output_dir" ]; then
    echo "$output_dir exists, deleting..."
    rm -fr $output_dir
fi

mkdir -p $output_dir

image_name="ev3dev/ev3dev-jessie-ev3-generic"
container_name="robertalab-service"

echo "delete old container..."
docker rm --force $container_name >/dev/null 2>&1 || true

echo "run new container to build..."
docker run \
    --volume "$build_dir:/build" \
    --volume "$output_dir:/output" \
    --workdir /build \
    --name $container_name \
    --tty \
    --detach \
    $image_name tail

echo "setup container build environment..."
# docker exec --tty $container_name apt-get install -y devscripts build-essential lintian
docker exec --tty $container_name /bin/bash -c "sudo apt-get update && \
    sudo apt-get install -y devscripts build-essential lintian && \
    sudo apt-get install -y python3-all dh-systemd python3-httpretty && \
    cd /build/robertalab-ev3dev && \
    debuild -us -uc && \
    cp ../*.deb /output/"
