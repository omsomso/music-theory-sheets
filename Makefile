# Build every sheet. Needs macOS (WebKit) with the Xcode command line tools for swiftc,
# Python 3.9+, and a network connection so Google Fonts load during rendering.
# docs/ is the GitHub Pages site: index.html plus <sheet>.html and <sheet>.pdf per sheet.

PY    ?= python3
BUILD := build
SITE  := docs

.PHONY: all test html pdf phone clean

all: test pdf phone

test:
	$(PY) -B -m unittest discover -s tests

html:
	@mkdir -p $(BUILD)
	rm -f $(BUILD)/*.html
	$(PY) -B src/build.py $(BUILD)

$(BUILD)/render: src/render.swift
	@mkdir -p $(BUILD)
	swiftc -O $< -o $@

$(BUILD)/phone_check: src/phone_check.swift
	@mkdir -p $(BUILD)
	swiftc -O $< -o $@

# Renders each sheet's A4 pages (fails if any page overflows) and refreshes the docs/ site.
pdf: html $(BUILD)/render
	@mkdir -p $(SITE)
	@set -e; for f in $(BUILD)/*-print.html; do \
	  s=$$(basename "$$f" -print.html); echo "== $$s"; \
	  $(BUILD)/render "$(CURDIR)/$$f" "$(CURDIR)/$(SITE)/$$s.pdf" "$(CURDIR)/$(BUILD)/$$s-page"; \
	  cp "$(BUILD)/$$s-preview.html" "$(SITE)/$$s.html"; \
	done
	cp $(BUILD)/index.html $(SITE)/index.html
	touch $(SITE)/.nojekyll

# Loads each sheet's web version at 390 px wide; fails if anything sticks out sideways.
phone: html $(BUILD)/phone_check
	@set -e; for f in $(BUILD)/*-preview.html; do \
	  s=$$(basename "$$f" -preview.html); echo "== $$s"; \
	  $(BUILD)/phone_check "$(CURDIR)/$$f" "$(CURDIR)/$(BUILD)/$$s-phone"; \
	done

clean:
	rm -rf $(BUILD)
