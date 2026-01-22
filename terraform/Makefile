# Makefile for Terraform operations
# This provides convenient shortcuts for common Terraform commands

.PHONY: help init plan apply destroy validate format clean

# Variables
API_ENDPOINT ?= 
TF_VARS = -var "api_endpoint=$(API_ENDPOINT)"

help: ## Show this help message
	@echo "Terraform Management Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Usage:"
	@echo "  make init                     # Initialize Terraform"
	@echo "  make plan API_ENDPOINT=xxx    # Show planned changes"
	@echo "  make apply API_ENDPOINT=xxx   # Apply changes"
	@echo "  make destroy API_ENDPOINT=xxx # Destroy infrastructure"

init: ## Initialize Terraform
	terraform init

plan: ## Show execution plan
	@if [ -z "$(API_ENDPOINT)" ]; then \
		echo "ERROR: API_ENDPOINT is required. Usage: make plan API_ENDPOINT=your-endpoint"; \
		exit 1; \
	fi
	terraform plan $(TF_VARS)

apply: ## Apply changes
	@if [ -z "$(API_ENDPOINT)" ]; then \
		echo "ERROR: API_ENDPOINT is required. Usage: make apply API_ENDPOINT=your-endpoint"; \
		exit 1; \
	fi
	terraform apply $(TF_VARS)

destroy: ## Destroy infrastructure
	@if [ -z "$(API_ENDPOINT)" ]; then \
		echo "ERROR: API_ENDPOINT is required. Usage: make destroy API_ENDPOINT=your-endpoint"; \
		exit 1; \
	fi
	terraform destroy $(TF_VARS)

validate: ## Validate Terraform configuration
	terraform validate

format: ## Format Terraform files
	terraform fmt -recursive

clean: ## Clean Terraform files
	rm -rf .terraform
	rm -f .terraform.lock.hcl
	rm -f terraform.tfstate*
	rm -f *.tfplan

upgrade: ## Upgrade providers
	terraform init -upgrade

output: ## Show outputs
	terraform output

refresh: ## Refresh state
	@if [ -z "$(API_ENDPOINT)" ]; then \
		echo "ERROR: API_ENDPOINT is required. Usage: make refresh API_ENDPOINT=your-endpoint"; \
		exit 1; \
	fi
	terraform refresh $(TF_VARS)

show: ## Show current state
	terraform show

graph: ## Generate dependency graph
	terraform graph | dot -Tpng > graph.png
	@echo "Graph saved to graph.png"
