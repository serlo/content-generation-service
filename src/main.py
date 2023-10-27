import logging.config
from pathlib import PurePath
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse
from langchain.chat_models import ChatOpenAI


log_config_file = f"{PurePath(__file__).parent}/logging.conf"
logging.config.fileConfig(log_config_file, disable_existing_loggers=True)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/health")
def get_health_status():
    return {"status": "ok"}


CAN_AUTHENTICATE: bool = False
try:
    load_dotenv(find_dotenv())
    chat = ChatOpenAI(temperature=0.4, model_name="gpt-4")
    CAN_AUTHENTICATE = True
except ValueError as e:
    logger.error(e)


@app.get("/execute", status_code=200, response_class=PlainTextResponse)
def execute(
    prompt: str,
    response: Response,
):
    logger.debug("PROMPT: %s", prompt)
    if CAN_AUTHENTICATE:
        llm_response = chat.predict(prompt)
        logger.debug("RESPONSE: %s", llm_response)
        return llm_response

    # 503: "The server is unavailable to handle this request right now."
    response.status_code = 503
    return "cannot use LLM"
