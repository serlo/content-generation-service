from enum import Enum
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

app = FastAPI()


@app.get("/health")
def get_health_status():
    return {"status": "ok"}


class Difficulty(Enum):
    LOW: str = "low"
    MEDIUM: str = "medium"
    HIGH: str = "high"


difficulty_to_german: dict[str, tuple[str, str]] = {
    "low": ("leicht", "Die Schüler haben Schwierigkeiten, abstrakt zu denken"),
    "medium": ("moderat", "Die Schüler haben gute Vorkenntnisse"),
    "high": ("schwer", "Die Schüler können gut abstrakt denken"),
}


class ExerciseType(Enum):
    MULTIPLE_CHOICE: str = "multiple choice"
    SINGLE_CHOICE: str = "single choice"
    SINGLE_WORD_SOLUTION: str = "single word solution"
    SINGLE_NUMBER_SOLUTION: str = "single number solution"


exercise_type_to_german: dict[str, str] = {
    "multiple choice": "Multiple Choice als JSON Objekt mit den Keys question, options und correct_options. Der Key options soll als Value eine Liste aller möglicher Antworten haben, der Key correct_options ein Liste mit den Indizes aller korrekten Antworten",
    "single choice": "Single Choice als JSON Objekt mit den Keys question, options und correct_option. Der Key options soll als Value eine Liste aller möglicher Antworten haben, der Key correct_options den Index der korrekten Antwort",
    "single word solution": "Antwortfeld mit einem Wort als Lösung, als JSON Objekt mit den Keys question und solution",
    "single number solution": "Antwortfeld mit einer Zahl als Lösung, als JSON Objekt mit den Keys question und solution",
}

has_key: bool = False
try:
    # read local .env file
    load_dotenv(find_dotenv())
    chat = ChatOpenAI(temperature=0.0)
    has_key = True
except ValueError as e:
    print(e)
    print(
        """As there is no key, \
this service now responds with the prompt instead of the output."""
    )


@app.get("/exercises")
# pylint: disable-next=R0913
def generate_exercises(
    subject: str,
    grade: int,
    difficulty: Difficulty,
    topic: str,
    goal: str,
    subtasks: int,
    previous_knowledge: str,
    exercise_type: ExerciseType,
):
    difficulty_and_meaning: tuple[str, str] = \
        difficulty_to_german[difficulty.value]
    template_string = """Erstelle für Schüler des {grade}. Jahrgangs \
im Fach {subject} \
zum Thema "{topic}" eine spannende Aufgabe{subtasks} vom Typ {exercise_type}. \
Formatiere alle Mathe-Symbole in LateX. \
Füge eine sinnvolle Überschrift für die Aufgabe unter dem Key heading hinzu, \
aus der das Thema der Aufgabe hervorgeht.
Die Schüler haben folgendes Vorwissen: {previous_knowledge}
Nach Bearbeiten der Aufgabe beherrschen die Schüler folgendes besser: {goal}
Verwende leichte Sprache. \
Das Anforderungsniveau soll {difficulty} sein. \
Beachte folgende  Charakterisierung der Schüler: {difficulty_text}. \
{json_reminder}
"""
    prompt_template = ChatPromptTemplate.from_template(template_string)
    prompt_to_generate_exercises = prompt_template.format_messages(
        subject=subject,
        grade=grade,
        difficulty=difficulty_and_meaning[0],
        difficulty_text=difficulty_and_meaning[1],
        topic=topic,
        goal=goal,
        exercise_type=exercise_type_to_german[exercise_type.value],
        subtasks=(
            ""
            if subtasks < 2
            else " mit " + str(subtasks) + " voneinander unabhängigen Teilaufgaben"
        ),
        json_reminder=(
            "Stelle sicher, dass deine Antwort ein unnamed JSON Objekt mit genau den genannten Keys ist"
            if subtasks < 2
            else "Stelle sicher, dass deine Antwort ein unnamed JSON Objekt ist, das den Key heading besitzt sowie den key subtasks, der eine Liste an unnamed Objekten enthält wovon jedes genau die bereits genannten Keys besitzt."
        ),
        previous_knowledge=previous_knowledge,
    )
    return (
        chat(prompt_to_generate_exercises)
        if has_key
        else prompt_to_generate_exercises[0].content
    )
