# backyardbrew-backend

## Run Development Server
To run the development server, make sure environment variables are set properly for configuration. For example:
```
export FLASK_APP="backend.py"
export APP_SETTINGS="development"
export FLASK_ENV=development # necessary separate from config.py to instantiate debugger/autoreload
export DATABASE_URL="postgresql://localhost/backyardbrew_dev_db"
export SQUARE_ACCESS_TOKEN="a-square-access-token"
export SQUARE_LOCATION_ID="a-square-location-id"
export SENDGRID_API_KEY="a-sendgrid-api-key"
```
`APP_SETTINGS` correspond to the dictionary at the bottom of the `config.py` file

## Run Tests
Run tests by running `python3 -m pytest`
