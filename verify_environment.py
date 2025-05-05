import sys
import importlib.metadata
from typing import Optional

def get_version(package_name: str) -> str:
    """Safely get package version using modern importlib.metadata"""
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return "Not installed"

print("Environment Verification Results:")
print(f"- Python: {sys.version.split()[0]}")

packages = [
    'numpy',
    'spotipy',
    'flask',
    'pymongo',
    'librosa',
    'scikit-learn',
    'pandas'
]

for pkg in packages:
    print(f"- {pkg.capitalize()}: {get_version(pkg)}")

try:
    from sklearn import __version__ as sklearn_version
    print(f"- Scikit-learn: {sklearn_version}")
except ImportError:
    pass