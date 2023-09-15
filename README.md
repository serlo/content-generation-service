# content-generation-service

The purpose if this service is to convert given arguments into a prompt, use an LLM and send the result back.

The service will receive queries from api.serlo.org which should receive them via GraphQL operation from frontend. 

The way through api.serlo.org is to check if a user is logged in and has the role required for the feature.

## Development

* Install the Python version in [.tool-versions](.tool-versions)
    * You may use [asdf](https://asdf-vm.com/) for the installation.
* Install the requirements using [pipenv](https://pipenv.pypa.io/en/latest/installation/#installing-pipenv)
* Run `pipenv shell` to activate the project's [virtual environment](https://docs.python.org/3/library/venv.html). 
* Run `pipenv install --dev` to install the development dependencies.
* Run `pipenv run lint` to run the linting.
* Run `pipenv run format` to format the code.
* Run `pipenv run type_check` to run the static type checker ([mypy](https://github.com/python/mypy)).


## Usage 

To run the service, go to the src/ folder and run
```
uvicorn main:app --reload --port=8080
```
where reload is optional to well reload the app when you change the code.

Or using Docker, simply run: `docker compose up -d`

To test an API endpoint, open your browser and send a request, for example
```
localhost:8080/exercises?subject=Mathe&grade=8&level=moderat&topic=Bruchrechnung&goal=Die Schüler können Brüche erweitern und kürzen.&category=ein Quiz&number_exercises=10&info="Das Quiz wird im Rahmen des Unterrichts an einer Mittelschule eingesetzt. Die Schülerinnen kennen die Grundlagen der Bruchrechnung."&exercise_types="Multiple Choice"
```
You can also check the docs to see all required arguments including their types without looking into the code:
```
http://localhost:8080/docs#/
```
Happy coding!

## Todo

We yet have to properly define the arguments and output format of the service.
