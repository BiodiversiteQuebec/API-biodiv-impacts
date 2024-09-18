### Installation
- Make sure you have Python 3.12 (maybe other versions will work but i tested with 3.12)

```
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```


### Running the project
Open a terminal in the root of the project. Run those commands :


1. To make sure you are in the virtual environment with the correct dependencies run:
```
source .venv/bin/activate

```

2. Now start the Fast API server
```
fastapi dev app/main.py
```
