"""
SISI LOLA MODAL - MINIMAL TEST
===============================
Ultra-minimal stub to test Modal deployment.
"""

import modal
from modal import App, Image
from typing import Dict

app = App("sisi-lola-test")

image = Image.debian_slim(python_version="3.11").pip_install("fastapi")


@app.function(image=image)
@modal.fastapi_endpoint(method="GET")
def hello() -> Dict[str, str]:
    """Simple hello endpoint"""
    return {
        "message": "Ẹ káàbọ̀! Sisi Lola is online!",
        "status": "success"
    }


@app.function(image=image)
@modal.fastapi_endpoint(method="POST")
def echo(request: Dict) -> Dict:
    """Echo endpoint for testing"""
    return {
        "you_said": request.get("message", "nothing"),
        "sisi_says": f"Omo! You said: {request.get('message', 'nothing')}",
        "status": "success"
    }
