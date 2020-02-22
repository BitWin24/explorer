#!/bin/env bash
while [ true ]; do
 rm -rf tmp/index.pid
 node scripts/sync.js index update
 sleep 5
done
