test:
	python3 -m unittest discover -s tests -v

lint:
	ruff check .
