# Employees Register
- Ayda Sholani

## Create envrionment
Create a environment at the project level!
```bash
$ py -m venv .venv
```
### Activate
```bash
$ source .venv/Scripts/activate
```
### Install requirements
```bash
$ pip install -r requirements.txt
```

## Create a .env file 
```python
LOCAL_DATABASE_URI = "database.sqlite"
```
## Create .flaskenv file for environment variables
```python
FLASK_APP = CodeCraftDatabase
FLASK_DEBUG = True
FLASK_PORT = 5000
```
## Styling

Open terminal in static folder
```bash
$ cd CodeCraft/static
```
Install dependencies
```bash
$ npm i
```

```bash
$ npm run compile_sass
```
# Create initial database with tables and data
```bash
$ flask init-db
```

### Run the app with the commando 
```bash
$ flask run 
```

