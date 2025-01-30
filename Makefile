lint:
	@echo
	isort --diff -c --skip-glob '*.venv' .
	@echo
	black .
	@echo
	flake8 .
	@echo

format_code:
	isort .
	black .
	flake8 .