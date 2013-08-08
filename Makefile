.PHONY: build clean reinstall


default: clean build

package_name=phantomcurl

build:
	python setup.py bdist_egg

clean:
	find . -name '*.pyc' -exec rm -v {} +;
	rm -rvf build/
	rm -rvf dist/
	rm -rvf $(package_name).egg-info/

reinstall: clean build
	pip uninstall --yes $(package_name)
	find dist/ -name '$(package_name)*.egg' | \
        head -n 1 | \
        xargs -n 1 easy_install
