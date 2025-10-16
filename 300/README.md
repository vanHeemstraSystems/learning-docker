# 300 - Learning Our Subject

# Learning Docker

A comprehensive Docker learning project built from a Cyber Security Engineer’s perspective. This repository contains a secure multi-tier web application that demonstrates Docker fundamentals, container orchestration, networking, security best practices, and real-world deployment scenarios.

## 🎯 Project Overview

This project implements a **Secure Task Management API** with the following components:

- **Backend API**: Python Flask application with security headers and rate limiting
- **Database**: PostgreSQL with persistent volume storage
- **Cache Layer**: Redis for session management and caching
- **Reverse Proxy**: Nginx with SSL/TLS termination and security configurations
- **Container Orchestration**: Docker Compose for multi-container management

## 🔐 Security Features Demonstrated

- Non-root container users
- Read-only root filesystems where possible
- Network isolation and segmentation
- Secret management via environment variables
- Security headers (CSP, HSTS, X-Frame-Options)
- Resource limits and quotas
- Minimal base images (Alpine Linux)
- No privileged containers

## 📁 Project Structure

```
Learning-Docker/
├── 300/README.md
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   └── config.py
├── nginx/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── ssl/
│       └── .gitkeep
└── scripts/
    └── init.sh
```

## 🚀 Getting Started

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

### Quick Start

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/Learning-Docker.git
cd Learning-Docker
```

1. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env with your configurations
```

1. **Build and run the containers**

```bash
docker-compose up --build
```

1. **Access the application**

- API: http://localhost/api/health
- Tasks endpoint: http://localhost/api/tasks

## 🐳 Docker Concepts Covered

### 1. Dockerfiles

- Multi-stage builds for optimized images
- Layer caching strategies
- Security hardening techniques
- Alpine-based minimal images

### 2. Docker Compose

- Multi-container orchestration
- Service dependencies and health checks
- Volume management (named volumes, bind mounts)
- Network creation and isolation
- Environment variable configuration

### 3. Networking

- Custom bridge networks
- Service discovery via DNS
- Port mapping and exposure
- Network isolation between services

### 4. Volumes & Data Persistence

- Named volumes for database persistence
- Bind mounts for development
- Volume permissions and ownership

### 5. Security Best Practices

- Running containers as non-root users
- Read-only root filesystems
- Dropping unnecessary capabilities
- Resource constraints (CPU, memory)
- Secret management

## 📚 Key Commands Reference

### Building Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend

# Build without cache
docker-compose build --no-cache
```

### Managing Containers

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Execute commands in running container
docker-compose exec backend sh

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Debugging & Inspection

```bash
# List running containers
docker ps

# Inspect container
docker inspect <container_id>

# View resource usage
docker stats

# Check networks
docker network ls
docker network inspect learning-docker_app-network
```

## 🧪 Testing the Application

### Health Check

```bash
curl http://localhost/api/health
```

### Create a Task

```bash
curl -X POST http://localhost/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Learn Docker","description":"Master containerization"}'
```

### List Tasks

```bash
curl http://localhost/api/tasks
```

### Get Specific Task

```bash
curl http://localhost/api/tasks/1
```

## 🔧 Advanced Topics

### Scaling Services

```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3
```

### Viewing Resource Constraints

```bash
docker stats
```

### Inspecting Volumes

```bash
docker volume ls
docker volume inspect learning-docker_postgres-data
```

## 🛡️ Security Considerations

1. **Never commit secrets**: Use `.env` files (gitignored) for sensitive data
1. **Regular updates**: Keep base images updated with security patches
1. **Minimal privileges**: Containers run as non-root users
1. **Network segmentation**: Services communicate only as needed
1. **Resource limits**: Prevent resource exhaustion attacks
1. **Image scanning**: Use `docker scan` to check for vulnerabilities

## 📖 Learning Path

1. ✅ Understand Docker basics (images, containers, volumes)
1. ✅ Write Dockerfiles with best practices
1. ✅ Use Docker Compose for multi-container apps
1. ✅ Implement networking and service discovery
1. ✅ Apply security hardening techniques
1. ✅ Monitor and debug containerized applications
1. ⬜ Learn Kubernetes for orchestration at scale
1. ⬜ Implement CI/CD pipelines with containers

## 🤝 Contributing

This is a personal learning repository. Feel free to fork and adapt for your own learning journey!

## 📝 License

MIT License - Feel free to use this for learning purposes.

## 🔗 Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
