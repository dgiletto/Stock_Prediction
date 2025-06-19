from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from forecast import forecast_7_day

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/forecast/{ticker}")
def get_forecast(ticker: str):
    try:
        forecast = forecast_7_day(ticker)
        return {"forecast": forecast}
    except Exception as e:
        return {"error": str(e)}
