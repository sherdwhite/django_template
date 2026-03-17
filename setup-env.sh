#!/bin/bash

# BookList Environment Setup Script
# Sets up environment files for different deployment scenarios

set -e

echo "🚀 BookList Environment Setup"
echo "================================"

# Function to create .env file from template
setup_env_file() {
    local template_file=$1
    local target_file=$2
    local description=$3

    if [ -f "$target_file" ]; then
        echo "⚠️  $target_file already exists. Skipping..."
        return
    fi

    if [ ! -f "$template_file" ]; then
        echo "❌ Template file $template_file not found!"
        return 1
    fi

    cp "$template_file" "$target_file"
    echo "✅ Created $target_file for $description"
}

echo "Select deployment type:"
echo "1) Local development"
echo "2) Production deployment"
echo "3) All environments"

read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "Setting up local development..."
        setup_env_file ".env.example" ".env" "local development"
        setup_env_file ".devcontainer/.env.example" ".devcontainer/.env" "DevContainer"
        echo "ℹ️  2FA codes will appear in console output (no email config needed)"
        ;;
    2)
        echo "Setting up production..."
        setup_env_file ".env.production.example" ".env.production" "production deployment"
        echo "⚠️  IMPORTANT: Configure email settings in .env.production for 2FA"
        echo "   Required: EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD"
        ;;
    3)
        echo "Setting up all environments..."
        setup_env_file ".env.example" ".env" "local development"
        setup_env_file ".devcontainer/.env.example" ".devcontainer/.env" "DevContainer"
        setup_env_file ".env.production.example" ".env.production" "production deployment"
        echo "ℹ️  Development: 2FA codes in console"
        echo "⚠️  Production: Configure email settings in .env.production"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo "✅ Setup complete! See docs/ENVIRONMENT_VARIABLES.md for details."
