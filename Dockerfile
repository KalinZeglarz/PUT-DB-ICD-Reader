FROM python:alpine3.7
COPY . /app
ENV icd_api_credentials_client_id=""
ENV icd_api_credentials_client_secret=""
ENV db_parameters_database="mysql+mysqlconnector"
ENV db_parameters_host="localhost:3306"
ENV db_parameters_user="root"
ENV db_parameters_password="root"
ENV server_parameters_host="0.0.0.0"
ENV server_parameters_port="5000"
ENV server_parameters_pool_size=10
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD PYTHONPATH=./icd_mapper python -m icd_mapper