from typing import List
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS: lets the grader's web page call your API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- The four layers (weakest to strongest) ----
DEFAULTS = {"port": 8000, "workers": 1, "debug": False,
            "log_level": "info", "api_key": "default-secret-000"}

YAML_LAYER = {"workers": 1, "log_level": "debug"}

DOTENV_LAYER = {            # NUM_WORKERS is renamed to "workers"
    "workers": "15",
    "debug": "false",
    "log_level": "warning",
    "api_key": "key-vn8uu728g7",
}

OS_ENV_LAYER = {            # APP_ prefix removed, lowercased
    "port": "8479",
    "log_level": "info",
    "api_key": "key-t5r32nazny",
}

def coerce(key, value):
    """Convert a raw value into the right type."""
    if key in ("port", "workers"):
        return int(value)
    if key == "debug":
        return str(value).strip().lower() in ("true", "1", "yes", "on")
    return str(value)

@app.get("/effective-config")
def effective_config(set: List[str] = Query(default=[])):
    config = dict(DEFAULTS)

    # Apply layers from weakest to strongest
    for layer in (YAML_LAYER, DOTENV_LAYER, OS_ENV_LAYER):
        for k, v in layer.items():
            config[k] = coerce(k, v)

    # CLI overrides: each looks like "port=9000"
    for item in set:
        if "=" not in item:
            continue
        k, v = item.split("=", 1)   # split only on the FIRST "="
        k = k.strip()
        try:
            config[k] = coerce(k, v)
        except ValueError:
            pass                     # ignore bad numbers

    config["api_key"] = "****"       # always mask
    return config