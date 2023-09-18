from enum import Enum
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, Query
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


difficulty_to_german: dict[str, tuple[str, str]] = {
    "low": ("leicht", "Die Schüler haben Schwierigkeiten, abstrakt zu denken"),
    "medium": ("moderat", "Die Schüler haben gute Vorkenntnisse"),
    "high": ("schwer", "Die Schüler können gut abstrakt denken"),
}


class ExerciseCategory(Enum):
    SINGLE: str = "eine Einzelaufgabe"
    QUIZ: str = "ein Quiz"
    TEST: str = "einen Test"


class ExerciseType(Enum):
    MULTIPLE_CHOICE: str = "Multiple Choice"
    SINGLE_CHOICE: str = "Single Choice"
    SINGLE_WORD_SOLUTION: str = "Lösung mit 1 Wort"
    SINGLE_NUMBER_SOLUTION: str = "Lösung mit 1 Zahl"


# read local .env file
load_dotenv(find_dotenv())
chat = ChatOpenAI(temperature=0.0)


@app.get("/exercises")
# pylint: disable-next=R0913
def generate_exercises(
    subject: str,
    grade: int,
    level: Difficulty,
    topic: str,
    goal: str,
    category: ExerciseCategory,
    number_exercises: int,
    previous_knowledge: str,
    exercise_types: list[ExerciseType] = Query(None),
):
    template_string = """
Erstelle für Schüler des {grade}. Jahrgangs \
im Fach {subject} \
zum Thema "{topic}" eine spannende Aufgabe \
mit {number_exercises} voneinander unabhängigen Teilaufgaben. \
Erstelle für jede Teilaufgabe eine Aufgabenstellung zur Berechnung, \
deren Lösung aus einer Zahl besteht. \
Füge eine sinnvolle Überschrift hinzu, \
aus der das Thema der Aufgabe hervorgeht. \
Die Schüler haben folgendes Vorwissen: {previous_knowledge}. \
Nach Bearbeiten der Aufgabe beherrschen die Schüler Folgendes besser: {goal}. \
Verwende leichte Sprache. \
Das Anforderungsniveau soll schwer sein. \
Beachte folgende  Charakterisierung der Schüler: \
Die Schüler können gut abstrakt denken. \
Beschreibe in ganzen Sätzen den Rechenweg, den die Schüler nutzen können, \
um die Aufgabe zu lösen, ohne das korrekte Ergebnis zu nennen. \
Nenne das korrekte Ergebnis. \
Beschreibe in ganzen Sätzen für eine Lehrkraft, \
welche Fehler die Schüler möglicherweise machen könnten. \
"""
    prompt_template = ChatPromptTemplate.from_template(template_string)
    prompt_to_generate_exercises = prompt_template.format_messages(
        subject=subject,
        grade=grade,
        level=level.value,
        topic=topic,
        goal=goal,
        category=category.value,
        exercise_types=", ".join([item.value for item in exercise_types]),
        number_exercises=number_exercises,
        previous_knowledge=previous_knowledge,
    )
    return chat(prompt_to_generate_exercises)
