from fastapi import FastAPI
import subprocess
import uuid
import os

app = FastAPI()

@app.post("/create-workout")
def create_workout():

    temp_file = f"/tmp/{uuid.uuid4()}.yaml"

    yaml_content = """
settings:
  deleteSameNameWorkout: true

workouts:
  api_test:
    - warmup: 5min
    - run: 10min
    - cooldown: 5min
"""

    with open(temp_file, "w") as f:
        f.write(yaml_content)

    subprocess.run(["python", "-m", "garmin_planner", temp_file])

    return {"status": "Workout created"}
