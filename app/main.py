from fastapi import FastAPI
from app.services import finding_matching_mkeywords

app = FastAPI()


# Example route that uses a service from 'services' package
@app.get("/matching-mkeywords")
def read_root():
    result = finding_matching_mkeywords.perform_some_logic()
    return {"message": "success", "result": result}
