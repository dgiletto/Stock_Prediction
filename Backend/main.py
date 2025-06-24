from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from forecast import forecast_and_eval

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/forecast/{ticker}")
def get_forecast(ticker: str):
    try:
        forecast = forecast_and_eval(ticker)
        return {"data": forecast}
    except Exception as e:
        return {"error": str(e)}
