# content-generation-service

The purpose of this service is to convert given arguments into a prompt, use an LLM and send the result back.

The service will receive queries from api.serlo.org which should receive them via GraphQL operation from frontend.

The way through api.serlo.org is to check if a user is logged in and has the role required for the feature.

## Development locally

- Install the Python version in [.tool-versions](.tool-versions)
  - You may use [asdf](https://asdf-vm.com/) for the installation.
- Install the requirements using [pipenv](https://pipenv.pypa.io/en/latest/installation/#installing-pipenv)
- Run `pipenv shell` to activate the project's [virtual environment](https://docs.python.org/3/library/venv.html).
- Run `pipenv install --dev` to install the development dependencies.
- Run `pipenv run lint` to run the linting.
- Run `pipenv run format` to format the code.
- Run `pipenv run type_check` to run the static type checker ([mypy](https://github.com/python/mypy)).

## Usage

### Setup

Copy the `.env.sample` file into a filed named `.env`, and change the `OPENAI_API_KEY` value to a valid one:

```bash
cp .env.sample .env
```

### Running the service

To run the service, run

```
uvicorn 'src.main:app' --reload --port=8082
```

where reload is optional to well reload the app when you change the code.

Or using Docker, simply run: `docker compose up -d`

### Testing

Your first step will likely be a look at

```
http://localhost:8082/docs#/
```

where you can use the "Try it out" button for an endpoint to test it or generate a request URL.

### Debugging

If you would like to see the debug level logs - for example the prompt sent to the LLM -, change the root log level in logging.conf from INFO to DEBUG.

Happy coding!
