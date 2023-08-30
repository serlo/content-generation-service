# content-generation-service

The purpose if this service is to convert given arguments into a prompt, use an LLM and send the result back.
The service will receive queries from api.serlo.org which should receive them via GraphQL operation from frontend. 
The way through api.serlo.org is to check if a user is logged in and has the role required for the feature.

## use/testing

To use the service, you have to install the requirements via
    pip install -r requirements.txt
and then go into the src/ folder and run
    uvicorn main:app --reload
where reload is optional to well reload the app when you change the code.
To test an API point, open your browser and send a request, for example
    localhost:8000/exercises?subject=Mathe&grade=8&level=moderat&topic=Bruchrechnung&goal=Die Schüler können Brüche erweitern und kürzen.&category=ein Quiz&number_exercises=10&info="Das Quiz wird im Rahmen des Unterrichts an einer Mittelschule eingesetzt. Die Schülerinnen kennen die Grundlagen der Bruchrechnung."&exercise_types="Multiple Choice"
You can also check the docs to see all required arguments including their types without looking into the code:
    http://localhost:8000/docs#/
Happy coding!

## to do

We yet have to properly define the arguments and output format of the service.
CI is missing yet.