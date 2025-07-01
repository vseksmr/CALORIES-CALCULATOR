import os.path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import requests
import models
import schemas
import database
import crud
import uvicorn
import json




def write_json(mancare,gramaj,kcal):

    if os.path.exists('history.json'):
        with open('history.json','r') as file:
            try:
                data=json.load(file)
                if not isinstance(data,list):
                    data=[]
            except json.JSONDecodeError:
                data=[]
    else:
        data=[]

    data.append({
        "food": mancare,
        "gramaj": gramaj,
        "kcal": kcal
    })

    with open('history.json','w+') as file:
        json.dump(data,file,indent=5)


def read_json():
    if os.path.exists('history.json'):
        with open('history.json', 'r') as file:
            try:
                data = json.load(file)
                if not isinstance(data, list):
                    data = []
            except json.JSONDecodeError:
                data = []
    else:
        data = []

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/calculeaza")
def calculeaza_calorii(input_data: schemas.FoodInput, db: Session = Depends(get_db)):
    food = crud.get_food_by_name(db, input_data.name.lower())

    if food:
        total_kcal = (input_data.grams / 100) * food.calories_per_100g
        mancare=food.name
        gramaj=input_data.grams
        kcal=total_kcal
        write_json(mancare,gramaj, kcal)
        return {"calorii": round(total_kcal, 2)}
    else:
        return get_food_from_usda(input_data.name, input_data.grams, db)

@app.get("/istoric")
def istoric():
    if os.path.exists('history.json'):
        with open('history.json', 'r') as file:
            try:
                data = json.load(file)
                if not isinstance(data, list):
                    data = []
            except json.JSONDecodeError:
                data = []
    else:
         data = []

    return data


def get_food_from_usda(name: str, grams: float, db: Session):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={name}&api_key=kM3Prclr9J9DNk53tHhjyccTq2FcTpwErvU1GyIV&pageSize=1&pageNumber=1"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if data.get("foods"):
            food_info = data["foods"][0]
            nutrients = food_info.get("foodNutrients")

            kcal = None
            for nutrient in nutrients:
                if nutrient["nutrientName"] == "Energy":
                    kcal = nutrient["value"]

            if kcal is not None:
                new_food = models.Food(name=name.lower(), calories_per_100g=kcal)
                db.add(new_food)
                db.commit()
                db.refresh(new_food)

                total_kcal = (grams / 100) * kcal

                mancare = name
                gramaj = grams
                kcal = total_kcal
                write_json(mancare, gramaj, kcal)

                return {"calorii": round(total_kcal, 2)}
            else:
                raise HTTPException(status_code=404, detail="Calorii nu au fost găsite pentru acest aliment.")
        else:
            raise HTTPException(status_code=404, detail="Alimentul nu a fost găsit în API-ul USDA.")
    else:
        raise HTTPException(status_code=500, detail="Eroare la apelul API-ului USDA.")


@app.post("/adauga")
def adauga_aliment(food: schemas.FoodCreate, db: Session = Depends(get_db)):
    return crud.create_food(db, food.name.lower(), food.calories_per_100g)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
