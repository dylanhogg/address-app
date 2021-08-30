FROM public.ecr.aws/lambda/python:3.7

COPY model /opt/ml/model
COPY requirements.txt ./

RUN python3.7 -m pip install --upgrade pip
RUN python3.7 -m pip install -r requirements.txt -t .

COPY addressnet ./addressnet
COPY app.py ./

CMD ["app.lambda_handler"]
