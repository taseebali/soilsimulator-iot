#!/bin/bash
# Quick setup script for GCP VM
# Run this on your VM after cloning the repository

set -e  # Exit on error

echo "🌱 Smart Agriculture IoT - VM Setup Script"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo -e "${RED}❌ This script is designed for Linux systems${NC}"
    exit 1
fi

# Check if Docker is installed
echo -e "${YELLOW}🔍 Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker first:"
    echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "  sudo sh get-docker.sh"
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not available${NC}"
    echo "Please install Docker Compose plugin"
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed${NC}"

# Check Docker daemon is running
if ! sudo systemctl is-active --quiet docker; then
    echo -e "${YELLOW}⚠️  Docker daemon is not running. Starting...${NC}"
    sudo systemctl start docker
    sudo systemctl enable docker
fi

echo -e "${GREEN}✅ Docker daemon is running${NC}"
echo ""

# Navigate to project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}📁 Current directory: $(pwd)${NC}"
echo ""

# Create necessary directories
echo -e "${YELLOW}📂 Creating directories...${NC}"
mkdir -p docker/mosquitto/data
mkdir -p docker/mosquitto/log
chmod -R 777 docker/mosquitto/data
chmod -R 777 docker/mosquitto/log

echo -e "${GREEN}✅ Directories created${NC}"
echo ""

# Check if docker-compose.yml exists
if [ ! -f "docker/docker-compose.yml" ]; then
    echo -e "${RED}❌ docker-compose.yml not found${NC}"
    echo "Make sure you're in the project root directory"
    exit 1
fi

# Stop any existing containers
echo -e "${YELLOW}🛑 Stopping any existing containers...${NC}"
cd docker
docker compose down 2>/dev/null || true
echo ""

# Pull latest images
echo -e "${YELLOW}📥 Pulling Docker images...${NC}"
docker compose pull
echo ""

# Start services
echo -e "${YELLOW}🚀 Starting services...${NC}"
docker compose up -d
echo ""

# Wait for services to start
echo -e "${YELLOW}⏳ Waiting for services to start (30 seconds)...${NC}"
sleep 30

# Check container status
echo -e "${YELLOW}🔍 Checking container status...${NC}"
docker compose ps
echo ""

# Check if all containers are running
RUNNING_CONTAINERS=$(docker compose ps --filter "status=running" --format "{{.Service}}" | wc -l)
EXPECTED_CONTAINERS=4

if [ "$RUNNING_CONTAINERS" -eq "$EXPECTED_CONTAINERS" ]; then
    echo -e "${GREEN}✅ All $EXPECTED_CONTAINERS containers are running!${NC}"
else
    echo -e "${RED}❌ Only $RUNNING_CONTAINERS out of $EXPECTED_CONTAINERS containers are running${NC}"
    echo "Check logs with: docker compose logs"
fi
echo ""

# Get VM external IP
echo -e "${YELLOW}🌐 Detecting external IP address...${NC}"
EXTERNAL_IP=$(curl -s http://checkip.amazonaws.com || curl -s http://ifconfig.me || echo "Unable to detect")
echo -e "${GREEN}External IP: $EXTERNAL_IP${NC}"
echo ""

# Test MQTT locally
echo -e "${YELLOW}🧪 Testing MQTT broker locally...${NC}"
if docker exec mqtt_broker mosquitto_pub -h localhost -t "test/setup" -m "VM setup complete" &>/dev/null; then
    echo -e "${GREEN}✅ MQTT broker is working${NC}"
else
    echo -e "${RED}❌ MQTT broker test failed${NC}"
fi
echo ""

# Display service URLs
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "📊 Service URLs:"
echo "  Grafana:  http://$EXTERNAL_IP:3000 (admin/admin)"
echo "  InfluxDB: http://$EXTERNAL_IP:8086 (admin/smartfarm2025)"
echo "  MQTT:     mqtt://$EXTERNAL_IP:1883"
echo ""
echo "🔍 Check container logs:"
echo "  docker logs mqtt_broker -f"
echo "  docker logs telegraf -f"
echo "  docker logs influxdb -f"
echo "  docker logs grafana -f"
echo ""
echo "🔥 Firewall Rules Required:"
echo "  Port 1883 (MQTT) - for sensor data"
echo "  Port 3000 (Grafana) - for dashboard"
echo "  Port 8086 (InfluxDB) - optional, for direct DB access"
echo ""
echo "📝 Next Steps:"
echo "  1. Configure GCP firewall rules (see CLOUD_VM_SETUP.md)"
echo "  2. Test from local machine: Test-NetConnection $EXTERNAL_IP -Port 1883"
echo "  3. Run simulator: python soil_sensor_simulator.py --broker $EXTERNAL_IP"
echo "  4. Open Grafana: http://$EXTERNAL_IP:3000"
echo ""
echo -e "${GREEN}Happy farming! 🌱🚜${NC}"
