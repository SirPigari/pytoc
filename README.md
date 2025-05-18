# PYTOC

**Version:** 0.1.0a  
**Recommended Python Version:** 3.13+

**PYTOC** is a lightweight Python-to-C transpiler and compiler that converts Python source code into C, then compiles it into a native Windows executable using [Tiny C Compiler (TCC)](https://bellard.org/tcc/). It’s ideal for small scripts, educational tools, and standalone applications that don’t require a full Python runtime.

---

## ✨ Features

- Transpiles Python source code to C via custom AST traversal.
- Compiles C to Windows `.exe` files using TCC.
- Supports both **32-bit** and **64-bit** architectures.
- Offers optional debugging symbols and automatic execution.
- Minimal external dependencies.

---

## 📦 Installation

1. **Clone the repository**  
```
git clone https://github.com/yourusername/PYTOC.git
cd PYTOC
```

2. **Ensure the following:**
   - Python 3.13+ installed
   - TCC binaries available in:
     - `tcc/tcc-win32/`
     - `tcc/tcc-win64/`

3. **Install dependencies** (if any):  
```
pip install -r requirements.txt
```

---

## 🚀 Usage

 ```
python main.py <source_file.py> <output_file.exe> [compiler_flags] [--debug] [--arch=32|64] [--auto-run] [--version | -v] [--help | -h]
 ```

or (as executable):

 ```
pytoc <source_file.py> <output_file.exe> [compiler_flags] [--debug] [--arch=32|64] [--auto-run] [--version | -v] [--help | -h]
 ```

### 🧾 Arguments

| Argument                  | Description                                                |
|---------------------------|------------------------------------------------------------|
| `<source_file.py>`        | Python file to transpile and compile.                      |
| `<output_file.exe>`       | Desired output executable name.                            |
| `[compiler_flags]`        | Optional flags to pass to TCC (e.g., `-O2`).               |
| `--debug`                 | Include debugging information.                             |
| `--arch=32` / `--arch=64` | Set output architecture (defaults to current Python arch). |
| `--auto-run`              | Automatically run the compiled executable.                 |
| `--version`, `-v`         | Show version and toolchain info.                           |
| `--help`, `-h`            | Display help information.                                  |

---

### ✅ Examples

**Basic compilation (32-bit):**  
 ```
python main.py script.py output.exe --arch=32
 ```

**With debug info and auto-run:**  
 ```
python main.py script.py output.exe --debug --auto-run --arch=64
 ```

**Display version:**  
 ```
python main.py --version
 ```

---

## 🗂 Project Structure

- `main.py` — CLI logic and build flow.
- `PYTOCTranspiler.py` — AST-based transpiler from Python to C.
- `tcc/` — Contains 32-bit and 64-bit TCC compilers.
- `temp/` — Temporary directory for intermediate files.
- `include/` — C source files for custom functions.
- `headers/` — C header files for custom functions.
- `LICENSE` — Project license.
- `README.md` — Project documentation.
- `requirements.txt` — Python dependencies (if any).

---

## 📄 License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE) for details.

---

> ## ⚠️ Disclaimer
> PYTOC supports only a subset of Python features. It's not intended for full Python compatibility and is best suited for small-scale utilities, learning, and experimentation.
> Use at your own risk. Always test the generated executables thoroughly.