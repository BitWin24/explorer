#!/bin/env bash
while [ true ]; do
 sleep 10
 rm -rf tmp/index.pid
 node scripts/sync.js index update
done
