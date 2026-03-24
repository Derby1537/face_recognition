import os
import sys
import onnxruntime as ort
from insightface.app import FaceAnalysis

_app = None


def _models_root() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_face_app() -> FaceAnalysis:
    global _app
    if _app is None:
        providers = ort.get_available_providers()
        _app = FaceAnalysis(name="buffalo_l", root=_models_root(), providers=providers)
        _app.prepare(ctx_id=0, det_size=(640, 640))
    return _app
