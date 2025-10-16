#!/bin/bash

# Color codes for output

RED=’\033[0;31m’
GREEN=’\033[0;32m’
YELLOW=’\033[1;33m’
NC=’\033[0m’ # No Color

echo -e “${GREEN}===========================================${NC}”
echo -e “${GREEN}  Learning Docker - Initialization Script${NC}”
echo -e “${GREEN}===========================================${NC}\n”

# Check if Docker is installed

if ! command -v docker &> /dev/null; then
echo -e “${RED}Error: Docker is not installed${NC}”
echo “Please install Docker from https://docs.docker.com/get-docker/”
exit 1
fi

# Check if Docker Compose is installed

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
echo -e “${RED}Error: Docker Compose is not installed${NC}”
echo “Please install Docker Compose from https://docs.docker.com/compose/install/”
exit 1
fi

echo -e “${GREEN}✓ Docker is installed${NC}”
echo -e “${GREEN}✓ Docker Compose is installed${NC}\n”

# Create .env file if it doesn’t exist

if [ ! -f .env ]; then
echo -e “${YELLOW}Creating .env file from template…${NC}”
cp .env.example .env

```
# Generate random passwords
POSTGRES_PASS=$(openssl rand -base64 24 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 24 | head -n 1)
REDIS_PASS=$(openssl rand -base64 24 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 24 | head -n 1)
SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)

# Replace passwords in .env file
sed -i.bak "s/your_secure_password_here/$POSTGRES_PASS/" .env
sed -i.bak "s/your_redis_password_here/$REDIS_PASS/" .env
sed -i.bak "s/your_secret_key_here_use_random_string/$SECRET_KEY/" .env
rm .env.bak 2>/dev/null

echo -e "${GREEN}✓ Created .env file with secure random passwords${NC}\n"
```

else
echo -e “${YELLOW}⚠ .env file already exists, skipping creation${NC}\n”
fi

# Build and start containers

echo -e “${YELLOW}Building Docker images…${NC}”
docker-compose build

echo -e “\n${YELLOW}Starting containers…${NC}”
docker-compose up -d

# Wait for services to be healthy

echo -e “\n${YELLOW}Waiting for services to be ready…${NC}”
sleep 10

# Check service health

echo -e “\n${YELLOW}Checking service health…${NC}”
HEALTH_CHECK=$(curl -s http://localhost/api/health)

if [ $? -eq 0 ]; then
echo -e “${GREEN}✓ All services are running!${NC}\n”
echo -e “${GREEN}===========================================${NC}”
echo -e “${GREEN}  Application is ready!${NC}”
echo -e “${GREEN}===========================================${NC}\n”
echo -e “API Health: ${GREEN}http://localhost/api/health${NC}”
echo -e “Tasks API:  ${GREEN}http://localhost/api/tasks${NC}\n”
echo -e “Try this command to create your first task:”
echo -e “${YELLOW}curl -X POST http://localhost/api/tasks -H ‘Content-Type: application/json’ -d ‘{"title":"Learn Docker","description":"Master containerization"}’${NC}\n”
echo -e “View logs: ${YELLOW}docker-compose logs -f${NC}”
echo -e “Stop services: ${YELLOW}docker-compose down${NC}\n”
else
echo -e “${RED}✗ Services failed to start properly${NC}”
echo -e “Check logs with: ${YELLOW}docker-compose logs${NC}\n”
exit 1
fi
