import onnxruntime as ort
import insightface
from insightface.app import FaceAnalysis

_app = None


def get_face_app() -> FaceAnalysis:
    global _app
    if _app is None:
        providers = ort.get_available_providers()
        _app = FaceAnalysis(name="buffalo_l", providers=providers)
        _app.prepare(ctx_id=0, det_size=(640, 640))
    return _app
