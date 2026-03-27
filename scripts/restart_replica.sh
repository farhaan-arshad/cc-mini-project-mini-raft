#!/bin/bash
# Restarts a specific replica by name
#!/bin/bash

REPLICA=$1

if [ -z "$REPLICA" ]; then
  echo "Usage: ./restart_replica.sh <replica_name>"
  echo "Example: ./restart_replica.sh replica1"
  exit 1
fi

VALID=("replica1" "replica2" "replica3")
if [[ ! " ${VALID[@]} " =~ " ${REPLICA} " ]]; then
  echo "Invalid replica name. Choose from: replica1, replica2, replica3"
  exit 1
fi

echo "Restarting $REPLICA..."
docker restart $REPLICA
echo "$REPLICA restarted. It will rejoin the cluster and sync its log automatically."
