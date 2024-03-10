FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
COPY ./xmalplus/requirements.txt /code/xmalplus/requirements.txt

RUN pip install --no-cache-dir torch -i https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r /code/requirements.txt -r /code/xmalplus/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY ./xmalplus /code/xmalplus
COPY ./app /code/app

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
