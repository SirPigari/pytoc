import ast
import tokenize
from io import BytesIO
import os
import subprocess
import tempfile
import PYTOCTranspiler
import sys
import struct

REQUIRED_PYTHON_VERSION = "3.13"
VERSION = "0.1.0a"


def analyze_python_code(source_code):
    """
    Analyzes Python include code by tokenizing and parsing it.

    Args:
        source_code (str): The Python code to analyze.

    Returns:
        tuple: A tuple containing:
            - tokens (list of tuples): List of (token_type, token_string).
            - ast_tree (ast.AST): Parsed AST of the include code.
    """
    tokens = []
    g = tokenize.tokenize(BytesIO(source_code.encode('utf-8')).readline)
    for tok in g:
        if tok.type == tokenize.ENCODING:
            continue
        tokens.append((tokenize.tok_name[tok.type], tok.string))

    tree = ast.parse(source_code)

    return tokens, tree


def compile_c(source_code, output_file, compiler_flags=None, debug=False, arch='32'):
    """
    Compiles C include code using TCC.

    Args:
        source_code (str): The C include code to compile.
        output_file (str): The desired output binary file path.
        compiler_flags (list, optional): Additional flags to pass to TCC.
        debug (bool): If True, include debug symbols.
        arch (str): Target architecture mode ('32' or '64').

    Returns:
        tuple: (success: bool, message: str)
    """
    base_dir = os.path.abspath(os.path.dirname(__file__))

    tcc_path = os.path.abspath(os.path.join(base_dir, f"tcc/tcc-win{arch}/tcc.exe"))
    temp_dir = os.path.join(base_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    if not os.path.isfile(tcc_path):
        return False, f"TCC not found at {tcc_path}"

    try:
        with tempfile.NamedTemporaryFile(dir=temp_dir, delete=False, suffix='.c', mode='w', encoding='utf-8') as tmp:
            tmp.write(source_code)
            tmp_path = tmp.name
    except Exception as e:
        return False, f"Error creating temporary include file: {e}"

    output_file = os.path.abspath(output_file)

    cmd = [tcc_path, tmp_path, '-o', output_file]
    if compiler_flags:
        if not isinstance(compiler_flags, list):
            return False, "Compiler flags must be a list."
        cmd.extend(compiler_flags)
    if debug:
        cmd.append('-g')
        print(f"[DEBUG] Using TCC: {tcc_path}")
        print(f"[DEBUG] Temp include file: {tmp_path}")
        print(f"[DEBUG] Output file: {output_file}")
        print(f"[DEBUG] Command: {' '.join(cmd)}")
        if compiler_flags:
            print(f"[DEBUG] Compiler flags: {compiler_flags}")
        print(f"[DEBUG] TCC version: {os.popen(f'{tcc_path} -v').read()}")

    try:
        subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return True, f"Compilation successful: {output_file}"
    except subprocess.CalledProcessError as e:
        return False, f"Compilation failed:\n{e.output.decode()}"
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


def python_to_c(source_code, debug=False):
    """
    Converts Python include code to C code.

    Args:
        source_code (str): The Python code to convert.
        debug (bool): If True, print debug information.

    Returns:
        str: The converted C code.
    """
    tokens, tree = analyze_python_code(source_code)
    if debug:
        print("[DEBUG] AST:")
        print(ast.dump(tree, indent=4))
    transpiler = PYTOCTranspiler.PYTOCTranspiler()
    transpiler.debug = debug
    c_code = transpiler.visit(tree)["code"]
    print("[DEBUG] C code generated:")
    if debug:
        print("\n")
        lines = c_code.splitlines()
        pad = len(str(len(lines)))
        for i, line in enumerate(lines):
            print(f"{str(i + 1).rjust(pad)}:\t {line}")
        print("\n")
    return c_code


def compile_py_to_c(source_code, output_file, compiler_flags=None, debug=False, arch='32'):
    """
    Compiles Python include code to C and then compiles the C code to an executable.

    Args:
        source_code (str): The Python code to compile.
        output_file (str): The desired output binary file path.
        compiler_flags (list, optional): Additional flags to pass to TCC.
        debug (bool): If True, include debug symbols.
        arch (str): Target architecture mode ('32' or '64').

    Returns:
        tuple: (success: bool, message: str)
    """
    c_code = python_to_c(source_code, debug=debug)
    success, message = compile_c(c_code, output_file, compiler_flags=compiler_flags, debug=debug, arch=arch)
    return success, message


def main():
    args = sys.argv[1:]
    compiler_flags = []
    debug = False
    architecture = str(struct.calcsize("P") * 8)
    auto_run = False
    if "-h" in args or "--help" in args:
        print("Usage: python main.py <source_file.py> <output_file.exe> [compiler_flags] [--debug] [--arch <32|64>] [--auto-run] [--version | -v]")
        sys.exit(0)
    if "-v" in args or "--version" in args:
        tcc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), f"tcc/tcc-win{architecture}/tcc.exe"))
        print(f"Version: {VERSION}, Recommended Python version: {REQUIRED_PYTHON_VERSION} (or higher), TCC version: {os.popen(f'{tcc_path} -v').read().removeprefix('tcc version ').removesuffix("\n")}")
        print(f"Python version: {sys.version}")
        print(f"Architecture: {architecture}-bit")
        print(f"TCC path: {tcc_path}")
        print(f"Using python at {sys.executable}")
        sys.exit(0)
    if len(args) < 2:
        print("Error: Missing arguments. Use -h or --help for usage.")
        sys.exit(1)
    source_file = args[0]
    output_file = args[1]
    for arg in args[2:]:
        if arg.startswith("--"):
            if arg == "--debug":
                debug = True
            elif arg.startswith("--arch"):
                architecture = arg.split("=")[1]
            elif arg == "--auto-run":
                auto_run = True
            else:
                print(f"Error: Unknown argument '{arg}'.")
                sys.exit(1)
        elif arg.startswith("-"):
            compiler_flags.append(arg)
        else:
            compiler_flags.append(arg)

    if not os.path.isfile(source_file):
        print(f"Error: Source file '{source_file}' not found.")
        sys.exit(1)

    if not os.path.splitext(output_file)[1]:
        output_file += ".exe"

    if architecture not in ['32', '64']:
        print("Error: Architecture must be '32' or '64'.")
        sys.exit(1)

    with open(source_file, 'r', encoding='utf-8') as f:
        source_code = f.read()
    if debug:
        print("[DEBUG] Source code:")
        print(source_code)

    try:
        success, message = compile_py_to_c(source_code, output_file, compiler_flags=compiler_flags, debug=debug, arch=architecture)
    except Exception as e:
        success = False
        message = f"{os.path.abspath(source_file)}: {e.__class__.__name__}: {e}"
    print(f"{message}")

    if not success:
        sys.exit(1)

    if auto_run:
        print(f"Running the compiled program: {output_file}")
        try:
            subprocess.run([output_file], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running the compiled program: {e}")
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
    sys.exit(0)