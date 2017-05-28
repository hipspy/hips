# Makefile with some convenient quick ways to do common things

PROJECT = hips

help:
	@echo ''
	@echo ' Gammapy available make targets:'
	@echo ''
	@echo '     help             Print this help message (the default)'
	@echo ''
	@echo '     test             Run tests'
	@echo '     code-analysis    Run static code analysis'
	@echo '     doc-show         Open local HTML docs in browser'
	@echo ''
	@echo '     clean            Remove generated files'
	@echo '     clean-repo       Remove all untracked files and directories (use with care!)'
	@echo ''
	@echo '     trailing-spaces  Remove trailing spaces at the end of lines in *.py files'
	@echo ''
	@echo ' Note that most things are done via `python setup.py`, we only use'
	@echo ' make for things that are not trivial to execute via `setup.py`.'
	@echo ''
	@echo ' Common `setup.py` commands:'
	@echo ''
	@echo '     python setup.py --help-commands'
	@echo '     python setup.py install'
	@echo '     python setup.py develop'
	@echo '     python setup.py test -V'
	@echo '     python setup.py test --help # to see available options'
	@echo '     python setup.py build_docs # use `-l` for clean build'
	@echo ''
	@echo ' More info:'
	@echo ''
	@echo ' * hips code: https://github.com/hipspy/hips'
	@echo ' * hips docs: https://hips.readthedocs.io'
	@echo ''

test:
	python -m pytest hips

# TODO: add flake8 and pylint
# TODO: activate mypy testing. Fix or configure to ignore these issues:
# https://travis-ci.org/hipspy/hips/jobs/236913996#L694
#	python -m mypy hips
code-analysis:
	python -m pycodestyle hips --count

doc-show:
	open docs/_build/html/index.html

clean:
	rm -rf build dist docs/_build docs/api htmlcov MANIFEST hips.egg-info .coverage .cache
	find . -name "*.pyc" -exec rm {} \;
	find . -name "*.so" -exec rm {} \;
	find hips -name '*.c' -exec rm {} \;
	find . -name __pycache__ | xargs rm -fr

clean-repo:
	@git clean -f -x -d

trailing-spaces:
	find $(PROJECT) docs -name "*.py" -exec perl -pi -e 's/[ \t]*$$//' {} \;
	find $(PROJECT) docs -name "*.rst" -exec perl -pi -e 's/[ \t]*$$//' {} \;

conda:
	python setup.py bdist_conda
