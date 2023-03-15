
## Getting Started

![Default Home View](./Screenshot.png?raw=true "Title")

Setup project environment with python -m venv myenv.

```bash
$ python -m venv myenv
$ source myenv/Scripts/activate
$ pip install -r requirements.txt

# You may want to change the name `projectname`.
$ django-admin startproject projectname

$ cd projectname/
$ python manage.py migrate
$ python manage.py runserver
```
