#!/bin/bash
# Finds and kills the current leader container
#!/bin/bash

echo "Finding current leader..."

REPLICAS=("http://localhost:8001" "http://localhost:8002" "http://localhost:8003")
CONTAINERS=("replica1" "replica2" "replica3")

for i in "${!REPLICAS[@]}"; do
  REPLICA=${REPLICAS[$i]}
  CONTAINER=${CONTAINERS[$i]}

  RESPONSE=$(curl -s "$REPLICA/status")
  STATE=$(echo $RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin).get('state',''))" 2>/dev/null)

  if [ "$STATE" == "LEADER" ]; then
    echo "Leader found: $CONTAINER"
    echo "Killing $CONTAINER..."
    docker stop $CONTAINER
    echo "$CONTAINER stopped. New election should begin within 800ms."
    exit 0
  fi
done

echo "No leader found. All replicas may be down."
exit 1