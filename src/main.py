import logging.config
from pathlib import PurePath
from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, Response, HTTPException, status
from fastapi.responses import JSONResponse
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
    # See https://help.openai.com/en/articles/8555510-gpt-4-turbo
    chat = ChatOpenAI(
        model_name="gpt-4-1106-preview",
        temperature=0.4,
        response_format={"type": "json_object"},
    )
    CAN_AUTHENTICATE = True
except ValueError as e:
    logger.error(e)


@app.get("/execute", status_code=200, response_class=JSONResponse)
def execute(
    prompt: str,
    response: Response,
):
    logger.debug("PROMPT: %s", prompt)
    if not prompt or prompt.strip() == "":
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing prompt parameter")

    if CAN_AUTHENTICATE:
        llm_response = chat.predict(prompt)
        logger.debug("RESPONSE: %s", llm_response)
        return JSONResponse(content=llm_response)

    # 503: "The server is unavailable to handle this request right now."
    response.status_code = 503
    return JSONResponse(content={"message": "cannot use LLM"})
