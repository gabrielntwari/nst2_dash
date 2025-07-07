FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install dash plotly gunicorn pandas numpy dash-bootstrap-components openpyxl  # Add other packages
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:server"]
