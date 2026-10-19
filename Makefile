build:
	python -m build
	python -m zipfile -l dist/*.whl
