#!/bin/bash
set -ex

source oe-init-build-env /build/ /lora-gateway-os/bitbake/
bitbake lora-gateway-os-full
loraserver-prepare-deploy
