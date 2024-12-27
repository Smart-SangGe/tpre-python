#!/bin/bash

mkdir lib
mkdir include

cp -r gmssl/include include

mkdir gmssl/build
cd gmssl/build || exit
cmake ..
make
cd bin || exit
cp libgmssl.so libgmssl.so.3 libgmssl.so.3.1 ../../../lib
cp libsdf_dummy.so libsdf_dummy.so.3 libsdf_dummy.so.3.1 ../../../lib
cp libskf_dummy.so libskf_dummy.so.3 libskf_dummy.so.3.1 ../../../lib
sudo make install
