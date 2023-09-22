import logging
from enum import Enum
from pathlib import PurePath
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, Response
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

log_config_file = f"{PurePath(__file__).parent}/logging.conf"
logging.config.fileConfig(log_config_file, disable_existing_loggers=True)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/health")
def get_health_status():
    return {"status": "ok"}


class Difficulty(Enum):
    LOW: str = "low"
    MEDIUM: str = "medium"
    HIGH: str = "high"


difficulty_to_prompt_texts: dict[str, tuple[str, str]] = {
    "low": ("leicht", "Die Schüler haben Schwierigkeiten, abstrakt zu denken"),
    "medium": ("moderat", "Die Schüler haben gute Vorkenntnisse"),
    "high": ("schwer", "Die Schüler können gut abstrakt denken"),
}


class ExerciseType(Enum):
    MULTIPLE_CHOICE: str = "multiple choice"
    SINGLE_CHOICE: str = "single choice"
    SINGLE_WORD_SOLUTION: str = "single word solution"
    SINGLE_NUMBER_SOLUTION: str = "single number solution"


exercise_type_to_prompt_texts: dict[str, tuple[str, str]] = {
    "multiple choice": (
        """vom Typ Multiple Choice, \
bei der es auch mehr als eine korrekte Antwort geben kann""",
        """type: "multiple_choice", question, options und correct_options. \
Der Key options soll als Value eine Liste von Antwortmöglichkeiten haben, \
der Key correct_options eine Liste mit den Indizes der korrekten Antworten""",
    ),
    "single choice": (
        """vom Typ Single Choice, bei der aus verschiedenen \
Antwortmöglichkeiten genau 1 korrekte Antwort ausgewählt werden muss""",
        """type: "single_choice", question, options und correct_options. \
Der Key options soll als Value eine Liste von Antwortmöglichkeiten haben, \
der Key correct_options den Index der korrekten Antwort""",
    ),
    "single word solution": (
        ", deren Lösung aus einem Wort besteht",
        "type: 'short_answer', question und correct_answer",
    ),
    "single number solution": (
        "zur Berechnung, deren Lösung aus einer Zahl besteht",
        "type: 'short_answer', question und correct_answer",
    ),
}

CAN_AUTHENTICATE: bool = False
try:
    load_dotenv(find_dotenv())
    chat = ChatOpenAI(temperature=0.4)
    CAN_AUTHENTICATE = True
except ValueError as e:
    logger.error(e)


@app.get("/exercises", status_code=200)
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
    response: Response,
):
    difficulty_and_meaning: tuple[str, str] = difficulty_to_prompt_texts[
        difficulty.value
    ]
    exercise_type_and_keys: tuple[str, str] = exercise_type_to_prompt_texts[
        exercise_type.value
    ]
    template_string = """Du bist eine kreative Lehrkraft, die spannende \
Aufgaben für Schüler des {grade}. Jahrgangs im Fach {subject} entwickelt. \
Erstelle zum Thema "{topic}" eine Aufgabe{subtasks} {exercise_type}. \
Füge eine sinnvolle Überschrift hinzu, aus der das Thema der Aufgabe \
hervorgeht. Die Schüler haben folgendes Vorwissen: {previous_knowledge}
Nach Bearbeiten der Aufgabe beherrschen die Schüler folgendes besser: {goal}
Verwende leichte Sprache. Das Anforderungsniveau soll {difficulty} sein. \
Beachte folgende Charakterisierung der Schüler: {difficulty_text}. \
Stelle die notierte Aufgabe zum Hochladen \
auf eine Lernplattform in einem unnamed JSON Objekt dar {json_description} \
{key_description}. Formatiere alle mathematischen Symbole in LateX. \
"""
    prompt_template = ChatPromptTemplate.from_template(template_string)
    prompt_to_generate_exercises = prompt_template.format_messages(
        subject=subject,
        grade=grade,
        difficulty=difficulty_and_meaning[0],
        difficulty_text=difficulty_and_meaning[1],
        topic=topic,
        goal=goal,
        exercise_type=exercise_type_and_keys[0],
        key_description=exercise_type_and_keys[1],
        subtasks=(
            ""
            if subtasks < 2
            else " mit " + str(subtasks) + " voneinander unabhängigen Teilaufgaben"
        ),
        json_description=(
            """mit dem Key heading und dem Key subtasks \
mit einer Liste von unnamed Objekten als Value, \
wovon jedes genau die folgenden Keys hat:"""
        ),
        previous_knowledge=previous_knowledge,
    )
    logger.debug('PROMPT: %s', prompt_to_generate_exercises[0].content)
    if CAN_AUTHENTICATE:
        llm_response = chat(prompt_to_generate_exercises)
        logger.debug('RESPONSE: %s', llm_response)
        return llm_response.content
    # 503: "The server is unavailable to handle this request right now."
    response.status_code = 503
    return "cannot use LLM"
