import os
import sys
import types

# Fix YOLO Ultralytics writable config dir
os.environ["YOLO_CONFIG_DIR"] = "/tmp"

# Polyfill pkg_resources for gdown (VietOCR) when setuptools is missing or pkg_resources is deprecated
try:
    import pkg_resources
except ImportError:
    pkg_res_mock = types.ModuleType("pkg_resources")
    class DummyDist:
        version = "5.2.0"
    pkg_res_mock.get_distribution = lambda name: DummyDist()
    sys.modules["pkg_resources"] = pkg_res_mock

import uvicorn
from main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    print(f"[Startup] CCCD OCR server running on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
