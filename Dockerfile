FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt

COPY sql_lineage.py /app/sql_lineage.py


RUN pip install -r /tmp/requirements.txt

EXPOSE 8501


CMD ["streamlit", "run", "sql_lineage.py", "--server.port=8501", "--server.address=0.0.0.0"]
