#!/bin/sh

# install script from https://github.com/cocogitto/cocogitto-action/blob/main/install.sh
CUR_DIR=$(pwd)
VERSION=6.1.0
TAR="cocogitto-$VERSION-x86_64-unknown-linux-musl.tar.gz"
BIN_DIR="$HOME/.local/bin"

mkdir -p "$BIN_DIR"
cd "$BIN_DIR" || exit
curl -OL https://github.com/cocogitto/cocogitto/releases/download/"$VERSION"/"$TAR"
tar --strip-components=1 -xzf $TAR x86_64-unknown-linux-musl/cog
cd "$CUR_DIR" || exit

# add to path as in https://github.com/cocogitto/cocogitto-action/blob/main/action.yml
echo "$HOME/.local/bin" >> $GITHUB_PATH