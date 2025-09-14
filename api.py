import requests
from settings import BASE_URL, TOKEN, AUTH_LOGIN, ADMIN_USERS, PRODUITS

def login(email, password):
    global TOKEN
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "mot_de_passe": password
        })
        data = resp.json()
        if resp.status_code == 200 and "token" in data:
            TOKEN = data["token"]
            return {"success": True, "token": TOKEN}
        return {"error": data.get("message", "Erreur de connexion")}
    except Exception as e:
        return {"error": str(e)}

def logout():
    global TOKEN
    TOKEN = None
    return {"success": True}

def get_headers():
    return {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

# --- Utilisateurs ---
def get_users():
    r = requests.get(f"{BASE_URL}/users", headers=get_headers())
    return r.json()

# --- Producteurs ---
def get_producteurs():
    r = requests.get(f"{BASE_URL}/producteurs", headers=get_headers())
    return r.json()

def valider_producteur(prod_id):
    r = requests.put(f"{BASE_URL}/producteurs/{prod_id}/valider", headers=get_headers())
    return r.json()

def refuser_producteur(prod_id):
    r = requests.put(f"{BASE_URL}/producteurs/{prod_id}/refuser", headers=get_headers())
    return r.json()
