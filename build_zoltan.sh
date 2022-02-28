#!/bin/sh

ZOLTAN_DIR=$1
ZOLTAN_VERSION="v3.901"
BUILD_DIR="/tmp"

URL="https://github.com/sandialabs/Zoltan"

Check()
{
    if [ $# -lt 1 ]; then
        echo "Usage: build_zoltan.sh TARGET_DIR"
        echo "Where TARGET_DIR is where the library and includes are installed."
        exit 1
    fi

    HEADER="$ZOLTAN_DIR/include/zoltan.h"
    if [ -f "$HEADER" ]; then
        echo "$HEADER already exists, skipping build."
        exit 0
    else
        mkdir $ZOLTAN_DIR
    fi
}

Download()
{
    FNAME=`basename $URL`
    git clone --depth=1 --branch $ZOLTAN_VERSION $URL $BUILD_DIR/$FNAME
}

Build()
{
    FNAME=`basename $URL`
    cd $BUILD_DIR/$FNAME
    mkdir build
    cd build
    ../configure --with-cflags=-fPIC --enable-mpi --prefix=$ZOLTAN_DIR
    make install
}

Check "$@"
Download
Build
