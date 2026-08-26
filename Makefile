VENV    ?= .venv
PY      := $(VENV)/bin/python
PIP     := $(VENV)/bin/pip
MKDOCS  := $(VENV)/bin/mkdocs

.DEFAULT_GOAL := help
.PHONY: help venv serve build check links check-all clean

help:  ## Show this help
	@grep -E '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

venv:  ## Create the virtualenv and install dependencies
	python3 -m venv $(VENV)
	$(PIP) install -q --upgrade pip
	$(PIP) install -q -r requirements.txt

serve: | $(VENV)  ## Live-reload preview at /cresis-remote-wiki/
	$(MKDOCS) serve

build: | $(VENV)  ## Build the site into site/
	$(MKDOCS) build --strict

# Fast, offline, deterministic. This is the one to run before every commit
# and in CI on every push.
check: | $(VENV)  ## Run all offline checks
	@echo "==> mkdocs strict build (broken internal links, config)"
	@# NOT --quiet: it drops the log to ERROR, and --strict aborts on WARNINGs,
	@# so --quiet silently disables broken-link detection.
	@$(MKDOCS) build --strict
	@echo "==> nav coverage (orphaned pages)"
	@$(PY) tools/check_orphans.py
	@echo "==> heading anchors (--strict does not check these)"
	@$(PY) tools/check_anchors.py
	@echo "==> shell scripts"
	@n=0; for f in $$(find docs -name '*.sh'); do \
	  bash -n "$$f" || exit 1; \
	  if command -v shellcheck >/dev/null 2>&1; then shellcheck "$$f" || exit 1; fi; \
	  echo "    ok  $$f"; n=$$((n+1)); \
	done; \
	command -v shellcheck >/dev/null 2>&1 || echo "    (shellcheck not installed: syntax only)"; \
	echo "    $$n script(s) checked"
	@echo ""
	@echo "All offline checks passed."

# Hits the network; slow and subject to other people's rate limits.
# Run before a release or on a schedule, not on every push.
links: | $(VENV)  ## Check outbound links (network, slow)
	@echo "==> OPR wiki links (via API, avoids rate limits)"
	@$(PY) tools/check_opr_links.py
	@echo "\n==> other external links"
	@$(PY) tools/check_external_links.py

check-all: check links  ## Offline checks plus link checking

clean:  ## Remove build output
	rm -rf site

$(VENV):
	@echo "No $(VENV) found. Run: make venv" >&2
	@exit 1
