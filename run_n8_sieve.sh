#!/bin/bash
# Launcher for n=8 twin prime class occupancy sieve
# Run with nohup so it survives session disconnects
echo "=== n=8 sieve launcher started at $(date) ==="
/home/rebecca/n8_twin_sieve_v2 2>&1
EXIT_CODE=$?
echo "=== n=8 sieve finished at $(date) with exit code $EXIT_CODE ==="
if [ -f /home/rebecca/n8_results_v2.json ]; then
  echo "Results file:"
  cat /home/rebecca/n8_results_v2.json
else
  echo "WARNING: Results file not found at /home/rebecca/n8_results_v2.json"
fi
exit $EXIT_CODE
