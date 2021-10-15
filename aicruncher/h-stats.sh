#!/usr/bin/env bash

# Read gpu stats
local temp=$(jq '.temp' <<< $gpu_stats)
local fan=$(jq '.fan' <<< $gpu_stats)
[[ $cpu_indexes_array != '[]' ]] && #remove Internal Gpus
    temp=$(jq -c "del(.$cpu_indexes_array)" <<< $temp) &&
    fan=$(jq -c "del(.$cpu_indexes_array)" <<< $fan)

# Read miner stats
local hs="[]"
local uptime=0
if [ -f "/hive/miners/custom/aicruncher/stats.json" ]; then
  khs=`jq .total /hive/miners/custom/aicruncher/stats.json`
  hs=`jq .rates /hive/miners/custom/aicruncher/stats.json`
  uptime=`jq .uptime /hive/miners/custom/aicruncher/stats.json`
else
  echo "No stats found"
  khs=0
fi

# Uptime
local ver=0.0.42
local hs_units="mhs"

# Performance
stats=$(jq -nc \
        --argjson hs "${hs}" \
        --arg total_khs "$khs" \
        --arg hs_units "$hs_units" \
        --argjson temp "$temp" \
        --argjson fan "$fan" \
        --arg uptime "$uptime" \
        --arg ver "$ver" \
        '{$total_khs, $hs, $hs_units, $temp, $fan, $uptime, $ver}')
