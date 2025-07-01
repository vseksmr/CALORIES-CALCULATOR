from pydantic import BaseModel

#asa primesc mancarea , cu nume si grame
class FoodInput(BaseModel):
    name: str
    grams: float

# asa creez mancare
class FoodCreate(BaseModel):
    name: str
    calories_per_100g: float

#validez datele prm de la frontend
# definesc modelele de intrare si iesire pt api
#basemodel - mosteneste toate modelele mele(eu am unu si ala e food)
#toate clasele care mostenesc basemodel pot fi fol ca tip de date in fast api
#sunt validate si convertite din json
