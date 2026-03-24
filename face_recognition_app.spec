# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_all

block_cipher = None

# Collect everything from onnxruntime (datas, binaries, hiddenimports)
datas = []
binaries = []
hiddenimports_extra = []
tmp_ret = collect_all('onnxruntime')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports_extra += tmp_ret[2]

# Explicitly copy the entire onnxruntime package directory (covers .pyd and DLLs on Windows)
try:
    import onnxruntime as _ort
    _ort_dir = os.path.dirname(_ort.__file__)
    datas += [(_ort_dir, 'onnxruntime')]
except ImportError:
    pass

datas += collect_data_files('insightface')

# include the insightface models from the project directory
_models_dir = os.path.join(os.path.dirname(os.path.abspath(SPEC)), 'ai_models')
if os.path.isdir(_models_dir):
    datas += [(_models_dir, 'ai_models')]

a = Analysis(
    ['run.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports_extra + [
        # FastAPI / Starlette
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.loops.asyncio',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'starlette.routing',
        # SQLAlchemy / PyMySQL
        'sqlalchemy.dialects.mysql',
        'sqlalchemy.dialects.mysql.pymysql',
        'pymysql',
        'pymysql.converters',
        # Pydantic
        'pydantic',
        'pydantic.deprecated.decorator',
        # insightface / onnxruntime
        'insightface',
        'onnxruntime',
        'cv2',
        # numpy
        'numpy',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'Cython',
        'tkinter', '_tkinter',
        'IPython', 'jupyter', 'notebook',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='face_recognition',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # keep console open to see server logs
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='face_recognition',
)
