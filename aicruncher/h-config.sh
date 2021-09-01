#!/usr/bin/env bash
cat > /hive/miners/custom/aicruncher/state.json <<EOF
{"id":"rig-$RIG_ID"}
EOF
cat > /hive/miners/custom/aicruncher/config.json << EOF
{"id":"rig-$RIG_ID", "name":"$WORKER_NAME"}
EOF