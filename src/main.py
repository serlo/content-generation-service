from enum import Enum
from fastapi import FastAPI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

app = FastAPI()


@app.get("/health")
def get_health_status():
    return {"status": "ok"}


class Difficulty(Enum):
    LOW: str = "leicht"
    MEDIUM: str = "moderat"
    HIGH: str = "knifflig"


class ExerciseCategory(Enum):
    SINGLE: str = "eine Einzelaufgabe"
    QUIZ: str = "ein Quiz"
    TEST: str = "einen Test"


class ExerciseType(Enum):
    MULTIPLE_CHOICE: str = "Multiple Choice"
    SINGLE_CHOICE: str = "Single Choice"
    GAP_TEXT: str = "Lückentext"
    TRUE_FALSE: str = "Wahr Falsch"
    MAPPING: str = "Zuordnung"
    FREE_TEXT: str = "Freitext"
    FACTUAL_TASK: str = "Sachaufgabe"
    SINGLE_WORD_SOLUTION: str = "Lösung mit 1 Wort"
    SINGLE_NUMBER_SOLUTION: str = "Lösung mit 1 Zahl"

# chat = ChatOpenAI(temperature=0.0)


@app.get("/exercises")
def generate_exercises(subject: str,
                       grade: int,
                       level: Difficulty,
                       topic: str,
                       goal: str,
                       category: ExerciseCategory,
                       exercise_types: list[ExerciseType],
                       number_exercises: int,
                       info: str
                       ):
    template_string = """
Erstelle {number_exercises} Aufgaben \
für {category} \
in {subject} \
in der Jahrgangsstufe {grade}. \
Der Schwierigkeitsgrad soll {level} sein. \
Das Ziel der Aufgaben ist: {goal} \
Folgende Aufgabentypen sollen hierbei enthalten sein: {exercise_types}. \
{info}
"""
    prompt_template = ChatPromptTemplate.from_template(template_string)
    prompt_to_generate_exercises = prompt_template.format_messages(
        subject=subject,
        grade=grade,
        level=level.value,
        topic=topic,
        goal=goal,
        category=category.value,
        exercise_types=', '.join([item.value for item in exercise_types]),
        number_exercises=number_exercises,
        info=info
        )
    # for first test just return the prompt instead of running it
    # generated_exercises = chat(prompt_to_generate_exercises)
    return prompt_to_generate_exercises[0].content
