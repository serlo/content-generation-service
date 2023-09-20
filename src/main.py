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
        """question, options and correct_options. \
The key options shall have as its value a list of all possible answers, \
the key correct_options a list with the indices of all correct answers""",
    ),
    "single choice": (
        """vom Typ Single Choice, bei der aus verschiedenen \
Antwortmöglichkeiten genau 1 korrekte Antwort ausgewählt werden muss""",
        """question, options and correct_options. \
The key options shall have as its value a list of all possible answers, \
the key correct_option the index of the correct answer""",
    ),
    "single word solution": (
        ", deren Lösung aus einem Wort besteht.",
        "question und solution",
    ),
    "single number solution": (
        "zur Berechnung, deren Lösung aus einer Zahl besteht."
        "question und solution"
    ),
}

has_key: bool = False
try:
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
    difficulty_and_meaning: tuple[str, str] = difficulty_to_prompt_texts[
        difficulty.value
    ]
    exercise_type_and_keys: tuple[str, str] = exercise_type_to_prompt_texts[
        exercise_type.value
    ]
    template_string = """Du bist eine kreative Lehrkraft, die spannende \
Aufgaben für Schüler des {grade}. Jahrgangs im Fach {subject} entwickelt. \
Erstelle zum Thema "{topic}" eine Aufgabe{subtasks} vom Typ {exercise_type}. \
Füge eine sinnvolle Überschrift hinzu, aus der das Thema der Aufgabe \
hervorgeht. Die Schüler haben folgendes Vorwissen: {previous_knowledge}\
Nach Bearbeiten der Aufgabe beherrschen die Schüler folgendes besser: {goal}
Verwende leichte Sprache. Das Anforderungsniveau soll {difficulty} sein. \
Beachte folgende  Charakterisierung der Schüler: {difficulty_text}. \
Beschreibe in ganzen Sätzen den Rechenweg, den die Schüler nutzen können, \
um die Aufgabe zu lösen, ohnedas korrekte Ergebnis zu nennen. \
Nenne das korrekte Ergebnis. Beschreibe in ganzen Sätzen für eine Lehrkraft, \
welche Fehler die Schüler möglicherweise machen könnten.\

After creating the exercises, put three backticks (```) and convert the \
exercises into an unnamed JSON object with {json_description} \
{key_description}. Format all maths symbols in LateX. \
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
            else " mit "
            + str(subtasks)
            + " voneinander unabhängigen Teilaufgaben"
        ),
        json_description=(
            "with precisely the keys heading, "
            if subtasks < 2
            else """that has the key heading as well as the key subtasks \
            that contains a list of unnamed objects \
            where each has precisely the keys"""
        ),
        previous_knowledge=previous_knowledge,
    )
    return (
        chat(prompt_to_generate_exercises)
        if has_key
        else prompt_to_generate_exercises[0].content
    )
