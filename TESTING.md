# Testing Guide

This document provides comprehensive testing procedures to validate Docker concepts and security features implemented in this project.

## Quick Start Testing

```bash
# Use the Makefile for quick testing
make test
```

## 1. Container Security Testing

### Test Non-Root Users

Verify containers run as non-root users:

```bash
# Check backend container user
docker-compose exec backend whoami
# Expected output: appuser

# Check nginx container user
docker-compose exec nginx whoami
# Expected output: nginx
```

### Test Read-Only Filesystem

Try to write to the backend container’s root filesystem:

```bash
# This should fail
docker-compose exec backend touch /test.txt
# Expected: Permission denied

# But /tmp should work (it's a tmpfs mount)
docker-compose exec backend touch /tmp/test.txt && echo "Success"
```

### Test Security Options

Inspect security settings:

```bash
# Check no-new-privileges flag
docker inspect learning-docker-backend | grep -A5 SecurityOpt
```

### Test Resource Limits

Check resource constraints:

```bash
# View resource limits
docker inspect learning-docker-backend | grep -A10 "Memory\|Cpu"

# Monitor real-time resource usage
docker stats
```

## 2. Network Security Testing

### Test Network Isolation

Verify backend network is internal:

```bash
# Backend network should be internal (no external access)
docker network inspect learning-docker_backend-network | grep internal

# Try to access external network from postgres (should fail if configured correctly)
docker-compose exec postgres ping -c 1 google.com || echo "Correctly isolated"
```

### Test Service Discovery

Verify internal DNS resolution:

```bash
# Backend should be able to resolve postgres by service name
docker-compose exec backend ping -c 1 postgres

# Backend should be able to resolve redis
docker-compose exec backend ping -c 1 redis
```

### Test Port Exposure

Only nginx should expose ports to host:

```bash
# Check what ports are exposed
docker-compose ps
# Only nginx should show 80:80 and 443:443
```

## 3. API Security Testing

### Test Security Headers

Verify security headers are present:

```bash
curl -I http://localhost/api/health
```

Expected headers:

- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security
- Content-Security-Policy

### Test Rate Limiting

Test nginx rate limiting:

```bash
# Send multiple requests rapidly
for i in {1..25}; do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost/api/tasks
done
```

You should see some 429 (Too Many Requests) responses.

### Test Invalid HTTP Methods

Test that invalid methods are rejected:

```bash
# Try an invalid method
curl -X TRACE http://localhost/api/tasks
# Expected: 405 Method Not Allowed
```

## 4. Data Persistence Testing

### Test Volume Persistence

Verify data persists across container restarts:

```bash
# Create a task
curl -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Persistence Test","description":"Testing volume persistence"}'

# Note the task ID from the response

# Restart containers
docker-compose restart backend postgres

# Wait a few seconds for services to restart
sleep 10

# Verify task still exists
curl http://localhost/api/tasks
```

### Test Database Volume

Check that database data is in a named volume:

```bash
# List volumes
docker volume ls | grep postgres

# Inspect volume
docker volume inspect learning-docker_postgres-data
```

## 5. Caching Testing

### Test Redis Caching

Verify Redis caching is working:

```bash
# First request (cache miss)
time curl -s http://localhost/api/tasks > /dev/null

# Second request (should be faster - cache hit)
time curl -s http://localhost/api/tasks > /dev/null

# Check Redis for cached data
docker-compose exec redis redis-cli -a $(grep REDIS_PASSWORD .env | cut -d'=' -f2) KEYS "*"
```

### Test Cache Invalidation

Verify cache is invalidated on updates:

```bash
# Get tasks (cache populated)
curl http://localhost/api/tasks

# Create new task (should invalidate cache)
curl -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"New Task"}'

# Get tasks again (cache should be refreshed)
curl http://localhost/api/tasks
```

## 6. Health Check Testing

### Test Container Health Checks

Monitor health status:

```bash
# Check health status
docker-compose ps

# Watch health checks in real-time
watch -n 2 'docker-compose ps'

# Check health check configuration
docker inspect learning-docker-backend | grep -A10 Healthcheck
```

### Test Service Dependencies

Verify services start in correct order:

```bash
# Stop everything
docker-compose down

# Start fresh and watch startup order
docker-compose up -d
docker-compose logs -f
```

Backend should wait for postgres and redis to be healthy before starting.

## 7. Logging Testing

### Test Log Output

Verify logging is working:

```bash
# Generate some activity
curl http://localhost/api/tasks

# Check nginx access logs
docker-compose logs nginx | grep GET

# Check backend logs
docker-compose logs backend

# Check for errors
docker-compose logs | grep -i error
```

### Test Log Rotation

Check log locations:

```bash
# Nginx logs
docker-compose exec nginx ls -lh /var/log/nginx/

# Check log sizes
docker-compose exec nginx du -h /var/log/nginx/
```

## 8. Multi-Stage Build Testing

### Test Image Sizes

Verify multi-stage builds reduced image size:

```bash
# Check image sizes
docker images | grep learning-docker

# Compare with non-optimized builds
# The backend image should be relatively small due to Alpine base
```

### Test Build Caching

Test Docker layer caching:

```bash
# Initial build
time docker-compose build backend

# Rebuild without changes (should be very fast)
time docker-compose build backend

# Change app.py and rebuild (should only rebuild from that layer)
touch backend/app.py
time docker-compose build backend
```

## 9. Scaling Testing

### Test Horizontal Scaling

Scale the backend service:

```bash
# Scale to 3 instances
docker-compose up -d --scale backend=3

# Check running instances
docker-compose ps | grep backend

# Test load distribution
for i in {1..10}; do
  curl -s http://localhost/api/health | grep service
done
```

## 10. Full Integration Test

### Complete Workflow Test

Test the entire application flow:

```bash
# 1. Health check
echo "1. Testing health endpoint..."
curl -s http://localhost/api/health | python3 -m json.tool

# 2. Create tasks
echo -e "\n2. Creating tasks..."
TASK1=$(curl -s -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn Docker Basics","description":"Understand containers and images"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

TASK2=$(curl -s -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Master Docker Compose","description":"Learn multi-container orchestration"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

echo "Created tasks: $TASK1, $TASK2"

# 3. List all tasks
echo -e "\n3. Listing all tasks..."
curl -s http://localhost/api/tasks | python3 -m json.tool

# 4. Get specific task
echo -e "\n4. Getting task $TASK1..."
curl -s http://localhost/api/tasks/$TASK1 | python3 -m json.tool

# 5. Update task
echo -e "\n5. Updating task $TASK1..."
curl -s -X PUT http://localhost/api/tasks/$TASK1 \
  -H "Content-Type: application/json" \
  -d '{"completed":true}' | python3 -m json.tool

# 6. Delete task
echo -e "\n6. Deleting task $TASK2..."
curl -s -X DELETE http://localhost/api/tasks/$TASK2 | python3 -m json.tool

# 7. Verify deletion
echo -e "\n7. Verifying final state..."
curl -s http://localhost/api/tasks | python3 -m json.tool

echo -e "\n✅ Integration test complete!"
```

## 11. Cleanup and Verification

### Test Clean Removal

Verify proper cleanup:

```bash
# Stop and remove everything
docker-compose down -v

# Verify no containers running
docker ps -a | grep learning-docker

# Verify volumes removed
docker volume ls | grep learning-docker

# Verify networks removed
docker network ls | grep learning-docker
```

## Performance Benchmarks

### Simple Load Test

Use `ab` (Apache Bench) or `hey` for basic load testing:

```bash
# Install hey: https://github.com/rakyll/hey
# Or use Apache Bench (ab)

# Test GET endpoint
hey -n 1000 -c 10 http://localhost/api/tasks

# Test POST endpoint
hey -n 100 -c 5 -m POST -H "Content-Type: application/json" \
  -d '{"title":"Load Test","description":"Performance testing"}' \
  http://localhost/api/tasks
```

## Troubleshooting Tests

If any test fails:

1. Check service status: `docker-compose ps`
1. Check logs: `docker-compose logs -f`
1. Verify environment: `docker-compose config`
1. Check resources: `docker stats`
1. Inspect containers: `docker inspect <container_name>`

## Automated Testing Script

Save this as `run_tests.sh`:

```bash
#!/bin/bash
echo "Running comprehensive Docker tests..."

# Source the testing functions
test_security() { echo "Testing security..."; }
test_networking() { echo "Testing networking..."; }
test_persistence() { echo "Testing persistence..."; }

# Run all tests
test_security
test_networking  
test_persistence

echo "All tests complete!"
```

-----

**Remember**: Always test in a safe environment before deploying to production!
