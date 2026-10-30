# BookList Docker Management
.PHONY: help build up down restart logs shell test migrate collectstatic superuser clean health prod-migrate

# Default target
help:
	@echo "BookList Docker Commands:"
	@echo "  build        - Build all services"
	@echo "  up          - Start all services"
	@echo "  down        - Stop all services"
	@echo "  restart     - Restart all services"
	@echo "  logs        - View logs (use SERVICE=name for specific)"
	@echo "  shell       - Access Django shell"
	@echo "  test        - Run tests"
	@echo "  migrate     - Run database migrations"
	@echo "  collectstatic - Collect static files"
	@echo "  superuser   - Create Django superuser"
	@echo "  health      - Check service health"
	@echo "  clean       - Clean up containers and volumes"
	@echo ""
	@echo "Production commands:"
	@echo "  prod-build   - Build production images"
	@echo "  prod-up      - Start production services"
	@echo "  prod-migrate - Run database migrations in production"
	@echo "  prod-down    - Stop production services"
	@echo ""
	@echo "Setup commands:"
	@echo "  setup       - Complete project setup"
	@echo "  dev-setup   - Quick development setup"

# Development commands
build:
	docker-compose build

up:
	docker-compose up

up-d:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
ifdef SERVICE
	docker-compose logs -f $(SERVICE)
else
	docker-compose logs -f
endif

shell:
	docker-compose exec booklist python manage.py shell

test:
	docker-compose exec booklist python manage.py test

migrate:
	docker-compose exec booklist python manage.py migrate

collectstatic:
	docker-compose exec booklist python manage.py collectstatic --noinput

superuser:
	docker-compose exec booklist python manage.py createsuperuser

health:
	@echo "Service Health Status:"
	@docker-compose ps
	@echo ""
	@echo "Container Status:"
	@docker ps --filter "name=booklist"

# Production commands
prod-build:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-migrate:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml run --rm booklist python manage.py migrate

prod-down:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# Cleanup commands
clean:
	docker-compose down -v
	docker system prune -f

clean-all:
	docker-compose down -v --remove-orphans
	docker system prune -af
	docker volume prune -f

# Setup commands
setup:
	@echo "🚀 Setting up BookList development environment..."
	./setup-env.sh
	make build
	make up-d
	@echo "⏳ Waiting for services to start..."
	sleep 15
	make migrate
	make collectstatic
	@echo "✅ Setup complete! Access your app at http://localhost:8000"

# Quick development setup
dev-setup:
	@echo "🚀 Quick development setup..."
	make up-d
	@echo "⏳ Waiting for services to start..."
	sleep 10
	make migrate
	make collectstatic
	@echo "✅ Development environment ready at http://localhost:8000"
