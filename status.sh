#!/bin/bash
# Check status of all bike data services

echo "🔍 Checking Bike Data Infrastructure Status..."
echo ""

# Check Docker Compose services
docker-compose ps

echo ""
echo "🏥 Health Status:"

# Check each service health
services=("db" "redis")

for service in "${services[@]}"; do
    if docker-compose ps -q $service > /dev/null 2>&1; then
        health=$(docker inspect --format='{{.State.Health.Status}}' $(docker-compose ps -q $service) 2>/dev/null || echo "no health check")
        status=$(docker inspect --format='{{.State.Status}}' $(docker-compose ps -q $service) 2>/dev/null || echo "unknown")

        if [ "$health" = "healthy" ] || [ "$health" = "no health check" ] && [ "$status" = "running" ]; then
            echo "✅ $service: $status ($health)"
        else
            echo "❌ $service: $status ($health)"
        fi
    else
        echo "❌ $service: not running"
    fi
done

echo ""
echo "📊 Resource Usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
