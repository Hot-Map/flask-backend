# Commands
## Run Server
```bash
python main.py
```

# Docker

## Docker Build
```bash
docker build -t flask-backend .
```

## Docker Run
```bash
docker run -p 5001:5001 flask-backend
```

## Export Environment
```bash
conda env export --no-builds > environment.yaml
```

## Import Environment
```bash
conda env create -n elec491 -f environment.yaml
```
```bash
conda install 'ffmpeg<5'
```
```bash
conda install ffmpeg=4.3 -c conda-forge
```
## For Windows
```bash
pip install soundfile
```
## For Linux
```bash
pip install sox
```