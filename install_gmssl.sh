#!/bin/bash

mkdir lib
mkdir include

cp -r gmssl/include include

mkdir gmssl/build
cd gmssl/build || exit
cmake ..
sudo make install
