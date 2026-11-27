PORT ?= 5173
ZIP  ?= dist/gns-site.zip
SITE := index.html en robots.txt sitemap.xml css js img

.PHONY: build serve package clean

build:
	python3 scripts/build_en.py

serve: build
	python3 -m http.server $(PORT)

package: build
	@mkdir -p $(dir $(ZIP))
	@rm -f $(ZIP)
	zip -rq $(ZIP) $(SITE) -x '*.DS_Store'
	@echo "Created $(ZIP)"

clean:
	rm -rf dist en
