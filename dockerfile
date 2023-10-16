FROM git.mamahaha.work/sangge/tpre:base

COPY src /app

COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

