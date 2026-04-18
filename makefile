setup:
	python -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt

pipeline:
	./venv/bin/python load_data.py
	./venv/bin/python part2.py
	./venv/bin/python part3a_analysis.py
	./venv/bin/python part3b_prediction.py
	./venv/bin/python part4.py

dashboard:
	./venv/bin/python dashboard.py