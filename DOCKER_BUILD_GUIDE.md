# Docker Build & Push Guide

## Prerequisites

- Docker installed on your machine
- Docker Hub account (create at https://hub.docker.com)
- Docker Desktop running

---

## Step 1: Test Rebuild Locally

First, rebuild the Docker image locally to test everything works:

```bash
cd C:\Scripts\CLAUDE\MCP\POSTGRES

# Stop any running containers
docker-compose down

# Clean up old images (optional)
docker system prune

# Rebuild fresh image from latest code
docker-compose up --build

# Should see:
# - Postgres container starting
# - MongoDB container starting
# - App container with automatic migration
# - "Starting API server..."
# - Running on http://localhost:5000
```

**Test in Browser:**
```
http://localhost:5000
```

You should see ReadVault with all 218 books loaded! ✅

---

## Step 2: Verify Everything Works

### Check Books Display
- Open http://localhost:5000
- See "Book Collection" table
- Verify Type column shows (E-Book, AudioBook, VideoBook, Book)
- Try adding a new book with YouTube source
- Verify Type auto-calculates

### Check Logs
```bash
docker-compose logs -f app
```

Should show:
```
Starting ReadVault...
Checking database migrations...
Database already has type column, skipping migration
Starting API server...
Running on http://localhost:5000
```

### Stop Containers
```bash
docker-compose down
```

---

## Step 3: Login to Docker Hub

```bash
docker login
```

Enter your Docker Hub username and password.

Output:
```
Login Succeeded
```

---

## Step 4: Build Docker Image with Version Tags

```bash
cd C:\Scripts\CLAUDE\MCP\POSTGRES

# Build with v1.1.0 tag (YouTube + Type feature)
docker build -t praveentv1996/readvault:v1.1.0 .

# Build with latest tag
docker build -t praveentv1996/readvault:latest .
```

Should see:
```
...
Step 12/13 : CMD ["/app/entrypoint.sh"]
...
Successfully built abc123def456
Successfully tagged praveentv1996/readvault:v1.1.0
Successfully tagged praveentv1996/readvault:latest
```

---

## Step 5: Push to Docker Hub

```bash
# Push v1.1.0
docker push praveentv1996/readvault:v1.1.0

# Output:
# The push refers to repository [docker.io/praveentv1996/readvault]
# v1.1.0: digest: sha256:abc123...
# Status: Pushed to docker.io/praveentv1996/readvault

# Push latest
docker push praveentv1996/readvault:latest

# Output:
# Status: Pushed to docker.io/praveentv1996/readvault
```

**Verify on Docker Hub:**
Visit: https://hub.docker.com/r/praveentv1996/readvault

You should see:
- `v1.1.0` tag ✅
- `latest` tag ✅

---

## Step 6: Test Pull from Docker Hub

Anyone (including you) can now pull the image:

```bash
# Pull specific version
docker pull praveentv1996/readvault:v1.1.0

# Pull latest version
docker pull praveentv1996/readvault:latest

# Run from Docker Hub image
docker-compose up
# (It will use the pulled image instead of building)
```

---

## Version Tags Reference

| Tag | Features | When to Use |
|-----|----------|------------|
| `v1.0.0` | Initial release | Never (deprecated) |
| `v1.1.0` | YouTube + Type | Production - stable |
| `latest` | Always newest | Development/Testing |

---

## Rollback to Previous Version

If something breaks, rollback:

```bash
# In docker-compose.yml, change:
image: readvault:latest
# To:
image: readvault:v1.0.0

# Then:
docker-compose down
docker-compose up
```

---

## Troubleshooting

### Image Push Fails: "Unauthorized"
```bash
# Solution: Login again
docker logout
docker login
docker push praveentv1996/readvault:v1.1.0
```

### Port Already in Use
```bash
# Kill process on port 5000
# Or change port in docker-compose.yml:
ports:
  - "5001:5000"  # Changed from 5000 to 5001
```

### Migration Fails
```bash
# Check logs:
docker-compose logs app

# If migration fails, it skips (marked as "|| true")
# But database may not have type column
# Fix manually:
docker-compose exec postgres psql -U postgres -d BOOK -c \
  "ALTER TABLE book ADD COLUMN type VARCHAR(50);"
```

### Clear Everything & Start Fresh
```bash
docker-compose down -v
docker system prune -a
docker-compose up --build
```

---

## What Gets Pushed to Docker Hub

When you push `praveentv1996/readvault:v1.1.0`, Docker Hub stores:

✅ Python 3.11 slim base image  
✅ All dependencies from requirements.txt  
✅ Latest code from your repo  
✅ Migration scripts  
✅ Frontend files  
✅ Entrypoint script for auto-migrations  

---

## Summary

After completing these steps:

✅ Docker image built locally with v1.1.0  
✅ Tested and verified working  
✅ Pushed to Docker Hub as `praveentv1996/readvault:v1.1.0`  
✅ Latest tag updated  
✅ Anyone can now pull and run: `docker pull praveentv1996/readvault:latest`

**You're done!** 🚀
