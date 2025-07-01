import requests
from sqlalchemy.orm import Session
import models

USDA_API_KEY = "kM3Prclr9J9DNk53tHhjyccTq2FcTpwErvU1GyIV"


def get_food_by_name(db: Session, name: str):
    return db.query(models.Food).filter(models.Food.name == name).first()


def create_food(db: Session, name: str, kcal: float):
    existing = get_food_by_name(db, name)
    if existing:
        existing.calories_per_100g = kcal
        db.commit()
        db.refresh(existing)
        return existing


    if kcal is None:
        kcal = get_food_usda(name)
        if kcal is None:
            return None

    new_food = models.Food(name=name, calories_per_100g=kcal)
    db.add(new_food)
    db.commit()
    db.refresh(new_food)
    return new_food


def get_food_usda(name: str):
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={name}&api_key={USDA_API_KEY}&pageSize=1&pageNumber=1"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("Răspuns API:", data)

            if data.get("foods"):
                food_info = data["foods"][0]
                nutrients = food_info.get("foodNutrients")

                print("Nutrienți:", nutrients)


                for nutrient in nutrients:
                    if nutrient["nutrientName"] == "Energy":
                        kcal = nutrient["value"]
                        print(f"Calorii găsite: {kcal}")
                        return kcal
            else:
                print("Nu am găsit niciun aliment cu acest nume.")
                return None
        else:
            print(f"Eroare API USDA: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Eroare la cererea API: {e}")
        return None
