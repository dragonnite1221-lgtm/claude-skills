# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from frontend_scaffolder_base import *  # noqa: F403,E402
# fmt: off
from frontend_scaffolder_p3 import _mod_cg0_0  # noqa: E402,E501
from frontend_scaffolder_p4 import _mod_cg0_1  # noqa: E402,E501
from frontend_scaffolder_p5 import _mod_cg0_2  # noqa: E402,E501
# fmt: on


def _mod_cg0_3():
    return {
        "REACT_APP": '''import { Button } from './components/ui';

function App() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold">Welcome</h1>
      <p className="mt-4 text-lg text-gray-600">
        Get started by editing src/App.tsx
      </p>
      <Button className="mt-6">Get Started</Button>
    </main>
  );
}

export default App;
''',
        "REACT_MAIN": '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
''',
        "EMPTY": "",
    }
FILE_CONTENTS = {**_mod_cg0_0(), **_mod_cg0_1(), **_mod_cg0_2(), **_mod_cg0_3()}
def generate_structure(
    base_path: Path,
    structure: Dict,
    dry_run: bool = False
) -> List[str]:
    """Generate directory structure recursively."""
    created_files = []

    for name, content in structure.items():
        current_path = base_path / name

        if isinstance(content, dict):
            # It's a directory
            if not dry_run:
                current_path.mkdir(parents=True, exist_ok=True)
            created_files.extend(generate_structure(current_path, content, dry_run))
        else:
            # It's a file
            if not dry_run:
                current_path.parent.mkdir(parents=True, exist_ok=True)
                file_content = FILE_CONTENTS.get(content, "")
                current_path.write_text(file_content)
            created_files.append(str(current_path))

    return created_files
