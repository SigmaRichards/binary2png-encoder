#!/bin/bash

PYW="/usr/bin/env python3"
ENC="src/encoder.py"
DEC="src/decoder.py"

if [[ $# -eq 0 ]]
then
	echo "Usage: ./img-encoder.sh [encode|decode] [...]"
	exit 1
fi

if [[ "$1" = "encode" ]] ; then
	TARGET=$ENC
fi
if [[ "$1" = "decode" ]] ; then
	TARGET=$DEC
fi
if [[ -z $TARGET ]] ; then
	echo "Unknown target: $1" && exit 1
fi

$PYW $TARGET ${@:2}
