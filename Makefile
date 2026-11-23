PORT ?= 5173
ZIP  ?= dist/gns-site.zip
SITE := index.html css js img

.PHONY: serve package clean

serve:
	python3 -m http.server $(PORT)

package:
	@mkdir -p $(dir $(ZIP))
	@rm -f $(ZIP)
	zip -rq $(ZIP) $(SITE) -x '*.DS_Store'
	@echo "Created $(ZIP)"

clean:
	rm -rf dist
