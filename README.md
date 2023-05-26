# Utilisation

Découverte du framework Flask

```sh
python3 -m venv venv
source /venv/bin/activate

pip install Flask SQLAlchemy

export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=true

flask initdb
flask run
```
