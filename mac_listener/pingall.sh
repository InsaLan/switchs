#!/bin/sh
while read ip; do
	fping -c 1 -t 150 "$ip"
done <ips.txt
