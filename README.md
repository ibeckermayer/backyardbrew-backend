# backyardbrew-backend

## Run Development Server
To run the development server, make sure environment variables are set properly for configuration. For example:
```
export FLASK_APP="backend.py"
export SECRET="my-super-secret"
export APP_SETTINGS="development"
export DATABASE_URL="postgresql://localhost/backyardbrew_dev_db"
```
`APP_SETTINGS` correspond to the dictionary at the bottom of the `config.py` file

## Run Tests
Run tests by running `python3 -m pytest`
