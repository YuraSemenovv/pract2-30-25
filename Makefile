CONFIG ?= config.json

run:
	python3 src/main.py $(CONFIG)

reverse:
	python3 src/main.py $(CONFIG) --reverse

test:
	python3 -m unittest discover -s tests
