.PHONY: build install clean uninstall reinstall

package_name=phantomcurl

default: clean build
reinstall: uninstall clean build install

build:
	python setup.py bdist_egg

install:
	find dist/ -name '$(package_name)*.egg' | \
        head -n 1 | \
        xargs -n 1 easy_install
	@if [ `which phantomjs` ]; then \
        echo okay, phantomjs binary is instaled; \
    else \
        echo IMPORTANT: phantomjs seems not to be installed, install phantomjs binary; \
    fi

uninstall:
	pip uninstall --yes $(package_name)

clean:
	find . -name '*.pyc' -exec rm -v {} +;
	rm -rvf build/
	rm -rvf dist/
	rm -rvf $(package_name).egg-info/

