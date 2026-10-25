.PHONY: install test lint run docker sample
install:
	pip install -r requirements-dev.txt
test:
	python -m pytest -q
lint:
	ruff check .
run:
	streamlit run streamlit_app.py
sample:
	python scripts/make_sample_data.py
docker:
	docker build -t uwazi-trace . && docker run --rm -p 8501:8501 uwazi-trace
