#!/bin/sh

dd if=$1 of=encPart bs=4 skip=1 count=262148
dd if=$1 of=plainPart bs=4 skip=262149

openssl enc -d -aes-256-cbc -in encPart -out decPart -K 34352423262364734A53562E2E2E32366931402A232C4023642D2D275B7B3240 -iv 6A323064616A27735E3B3A78732C2C7E

cat decPart plainPart > dec_$1

rm encPart plainPart decPart