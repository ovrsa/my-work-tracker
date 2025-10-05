PACKAGE_DIR=work_report
DOCKER_TAG=work-report:0.1.0

.PHONY: format
format:
	@uv run isort .
	@uv run black .

.PHONY: format-check
format-check:
	@uv run isort --check .
	@uv run black --check .

.PHONY: lint
lint:
	@uv run pylint -d C,R,fixme $(PACKAGE_DIR) tests main.py
	@uv run mypy --show-error-codes $(PACKAGE_DIR) tests main.py

.PHONY: test
test:
	@uv run pytest tests
	@uv run coverage-badge -f -o docs/img/coverage.svg

# .PHONY: lint-docker
# lint-docker:
# 	@hadolint ./Dockerfile

# .PHONY: build-docker
# build-docker:
# 	@docker build --no-cache -t $(DOCKER_TAG) .

# .PHONY: scan-docker
# scan-docker:
# 	@dockle $(DOCKER_TAG)
# 	@trivy image --ignore-unfixed $(DOCKER_TAG)

# .PHONY: scan-docker-for-actions
# scan-docker-for-actions:
# 	# -------------------- dockle -------------------- #
# 	@dockle --no-color -q $(DOCKER_TAG)
# 	# -------------------- trivy -------------------- #
# 	@trivy image --ignore-unfixed $(DOCKER_TAG)

# .PHONY: docker
# docker: lint-docker build-docker scan-docker

# TODO: add docker
.PHONY: pre-commit
pre-commit: format lint test

.PHONY: run
run:
	@uv run streamlit run main.py
