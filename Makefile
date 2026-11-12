CONFIG ?= config.json

run:
	python3 src/main.py $(CONFIG)

test:
	python3 -m unittest discover -s tests
