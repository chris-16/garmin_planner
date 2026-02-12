from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import subprocess
import uuid
import os

app = FastAPI()

# 1) Pon una API key simple para que nadie use tu endpoint
API_KEY = os.environ.get("API_KEY", "")

class CreateWorkoutRequest(BaseModel):
    email: str
    password: str
    yaml_content: str  # YAML completo compatible con garmin_planner

@app.get("/")
def health():
    return {"status": "API running"}

@app.post("/create-workout")
def create_workout(req: CreateWorkoutRequest, x_api_key: str = Header(None)):
    # Security (MVP-level)
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Escribimos un YAML temporal
    temp_file = f"/tmp/{uuid.uuid4()}.yaml"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(req.yaml_content)

    # Ejecutamos garmin_planner con ese YAML
    # OJO: garmin_planner espera secrets.yaml en carpeta garmin_planner/
    # Para multiusuario, vamos a generar secrets.yaml dinámico antes.
    secrets_path = os.path.join("garmin_planner", "secrets.yaml")
    secrets_content = f'email: "{req.email}"\npassword: "{req.password}"\n'
    with open(secrets_path, "w", encoding="utf-8") as f:
        f.write(secrets_content)

    # Ejecutar
    result = subprocess.run(
        ["python", "-m", "garmin_planner", temp_file],
        capture_output=True,
        text=True
    )

    # Limpiar (opcional MVP): borra secrets después de correr
    try:
        os.remove(secrets_path)
    except Exception:
        pass

    if result.returncode != 0:
        return {
            "status": "error",
            "stdout": result.stdout[-3000:],
            "stderr": result.stderr[-3000:]
        }

    return {"status": "ok", "stdout": result.stdout[-3000:]}
