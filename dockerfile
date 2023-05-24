FROM continuumio/miniconda3:latest

WORKDIR /flask-backend
COPY . /flask-backend

RUN conda create -n elec491 python=3.9 ipython

RUN conda run -n elec491 pip install -r requirements.txt

EXPOSE 5001

CMD ["conda", "run", "-n", "elec491", "python", "main.py"]
