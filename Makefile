# YouTube Archive Agent - Makefile
# Docker and native operations

.PHONY: help docker-build docker-up docker-down docker-logs docker-shell docker-test docker-daily native-run native-test clean cleanup verify-sync

# Docker
DOCKER = /usr/local/bin/docker
DOCKER_PATH = /Applications/Docker.app/Contents/Resources/bin:/usr/local/bin
export PATH := $(DOCKER_PATH):$(PATH)

# Colors
GREEN = \033[0;32m
YELLOW = \033[1;33m
NC = \033[0m # No Color

help:
	@echo "$(GREEN)YouTube Archive Agent - Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Docker Commands:$(NC)"
	@echo "  make docker-build     - Build Docker image"
	@echo "  make docker-up        - Start agent in background"
	@echo "  make docker-down      - Stop agent"
	@echo "  make docker-logs      - View logs (follow)"
	@echo "  make docker-shell     - Open shell in container"
	@echo "  make docker-test      - Run once (test mode)"
	@echo "  make docker-daily     - Run daily job (for cron)"
	@echo "  make docker-restart   - Restart container"
	@echo "  make docker-stats     - View resource usage"
	@echo ""
	@echo "$(YELLOW)Native Commands:$(NC)"
	@echo "  make native-run       - Run agent natively"
	@echo "  make native-test      - Test run (once)"
	@echo "  make native-deps      - Check dependencies"
	@echo ""
	@echo "$(YELLOW)Maintenance:$(NC)"
	@echo "  make clean            - Remove containers and volumes"
	@echo "  make cleanup          - Remove orphaned files"
	@echo "  make verify-sync      - Verify database vs Google Drive"
	@echo "  make update           - Update and rebuild"
	@echo "  make db-shell         - Open database shell"
	@echo "  make db-stats         - Show database statistics"

# Docker commands
docker-build:
	@echo "$(GREEN)Building Docker image...$(NC)"
	$(DOCKER) compose build

docker-up:
	@echo "$(GREEN)Starting YouTube Archive Agent...$(NC)"
	$(DOCKER) compose up -d
	@echo "$(GREEN)✓ Agent started. View logs with: make docker-logs$(NC)"

docker-down:
	@echo "$(GREEN)Stopping YouTube Archive Agent...$(NC)"
	$(DOCKER) compose down
	@echo "$(GREEN)✓ Agent stopped$(NC)"

docker-logs:
	@echo "$(GREEN)Viewing logs (Ctrl+C to exit)...$(NC)"
	$(DOCKER) compose logs -f

docker-shell:
	@echo "$(GREEN)Opening shell in container...$(NC)"
	$(DOCKER) compose exec youtube-archive bash

docker-test:
	@echo "$(GREEN)Running test (once)...$(NC)"
	$(DOCKER) compose exec youtube-archive python agent.py --config /app/config/my_config.py --once

docker-daily:
	@echo "$(GREEN)Running daily job...$(NC)"
	./run-daily.sh

docker-restart:
	@echo "$(GREEN)Restarting agent...$(NC)"
	$(DOCKER) compose restart
	@echo "$(GREEN)✓ Agent restarted$(NC)"

docker-stats:
	@echo "$(GREEN)Resource usage:$(NC)"
	$(DOCKER) stats youtube-archive-agent --no-stream

# Native commands
native-run:
	@echo "$(GREEN)Running agent natively...$(NC)"
	python3 agent.py --config my_config.py

native-test:
	@echo "$(GREEN)Running test (once)...$(NC)"
	python3 agent.py --config my_config.py --once

native-deps:
	@echo "$(GREEN)Checking dependencies...$(NC)"
	python3 agent.py --check-deps

# Maintenance
clean:
	@echo "$(GREEN)Cleaning up Docker resources...$(NC)"
	$(DOCKER) compose down -v
	@echo "$(GREEN)✓ Cleaned$(NC)"

update:
	@echo "$(GREEN)Updating and rebuilding...$(NC)"
	git pull
	$(DOCKER) compose down
	$(DOCKER) compose build
	$(DOCKER) compose up -d
	@echo "$(GREEN)✓ Updated and restarted$(NC)"

db-shell:
	@echo "$(GREEN)Opening database shell...$(NC)"
	$(DOCKER) compose exec youtube-archive sqlite3 /app/data/archive.db

db-stats:
	@echo "$(GREEN)Database statistics:$(NC)"
	@$(DOCKER) compose exec youtube-archive sqlite3 /app/data/archive.db \
		"SELECT COUNT(*) as 'Total Videos' FROM videos; \
		 SELECT SUM(file_size)/1024/1024 as 'Total Size (MB)' FROM videos WHERE file_size IS NOT NULL; \
		 SELECT MAX(downloaded_at) as 'Last Download' FROM videos;"

# Setup helpers
setup-config:
	@echo "$(GREEN)Setting up configuration...$(NC)"
	@if [ ! -f my_config.py ]; then \
		cp config.example.py my_config.py; \
		echo "$(GREEN)✓ Created my_config.py - please edit it with your settings$(NC)"; \
	else \
		echo "$(YELLOW)my_config.py already exists$(NC)"; \
	fi

setup-data:
	@echo "$(GREEN)Creating data directory...$(NC)"
	@mkdir -p data
	@echo "$(GREEN)✓ Data directory ready$(NC)"

setup: setup-config setup-data
	@echo "$(GREEN)✓ Setup complete!$(NC)"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Edit my_config.py and set your WATCHLIST_URL"
	@echo "  2. Configure rclone: rclone config"
	@echo "  3. Build and run: make docker-build && make docker-up"

# Cleanup and verification
cleanup:
	@echo "$(GREEN)Running cleanup...$(NC)"
	./cleanup.sh

verify-sync:
	@echo "$(GREEN)Verifying sync between database and Google Drive...$(NC)"
	python3 verify-sync.py
