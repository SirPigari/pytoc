import ast
import os
import hashlib

class PYTOCTranspiler:
    def __init__(self, debug=False):
        self.debug = debug
        self.indent_level = 0
        self.indent_str = "    "
        self.temp_num = 0

        self.c_code = []
        self.imports = []
        self.func_defs = []
        self.variables = {}
        self.constants = {}
        self.functions = {}
        self.tmps = {}

        import os

        self.function_map = {
            "print": {
                "lib": f"\"{os.path.abspath('source/_global.c')}\"",
                "temp": {
                    "prefix": "_print",
                    "code": f"Value {{}}[{{ temp_name }}] = {{}}"
                },
                "format": "print(make_list({3}, {0}), {1}, {2})",
                "type": "Value",
                "args": [
                    {"name": "args", "type": "Value", "default": "create_string(\"\")"},
                    {"name": "sep", "type": "Value", "default": "create_string(\" \")"},
                    {"name": "end", "type": "Value", "default": "create_string(\"\\n\")"},
                    {"name": "list_len", "type": "int", "default": "0", "code": "len(args)"},
                ]
            },
            "int": {
                "lib": f"\"{os.path.abspath('source/runtime.c')}\"",
                "format": "to_int({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "str": {
                "lib": f"\"{os.path.abspath('source/runtime.c')}\"",
                "format": "to_string({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "len": {
                "lib": f"\"{os.path.abspath('source/runtime.c')}\"",
                "format": "len({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "abs": {
                "lib": f"\"{os.path.abspath('source/runtime.c')}\"",
                "format": "abs_val({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "max": {
                "lib": f"\"{os.path.abspath('source/runtime.c')}\"",
                "format": "max_val({0})",
                "type": "Value",
                "args": [{"name": "list", "type": "Value"}],
            },
            "min": {
                "lib": f"\"{os.path.abspath('source/runtime.c')}\"",
                "format": "min_val({0})",
                "type": "Value",
                "args": [{"name": "list", "type": "Value"}],
            },
            "sum": {
                "lib": f"\"{os.path.abspath('source/runtime.c')}\"",
                "format": "sum_val({0})",
                "type": "Value",
                "args": [{"name": "list", "type": "Value"}],
            },
            "bool": {
                "lib": f"\"{os.path.abspath('source/runtime.c')}\"",
                "format": "bool_val({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "ord": {
                "lib": f"\"{os.path.abspath('source/runtime.c')}\"",
                "format": "ord_val({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "chr": {
                "lib": f"\"{os.path.abspath('source/runtime.c')}\"",
                "format": "chr_val({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "range": {
                "lib": f"\"{os.path.abspath('source/runtime.c')}\"",
                "format": "range_stop({0})",
                "type": "Value",
                "args": [{"name": "stop", "type": "int"}],
            },
            "range_start_stop": {
                "lib": f"\"{os.path.abspath('source/runtime.c')}\"",
                "format": "range_start_stop({0}, {1})",
                "type": "Value",
                "args": [{"name": "start", "type": "int"}, {"name": "stop", "type": "int"}],
            },
            "reversed": {
                "lib": f"\"{os.path.abspath('source/runtime.c')}\"",
                "format": "reversed_val({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "upper": {
                "lib": f"\"{os.path.abspath('source/runtime.c')}\"",
                "format": "upper_val({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "lower": {
                "lib": f"\"{os.path.abspath('source/runtime.c')}\"",
                "format": "lower_val({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "isinstance": {
                "lib": f"\"{os.path.abspath('source/runtime.c')}\"",
                "format": "isinstance_val({0}, {1})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}, {"name": "type", "type": "ValueType"}],
            },
            "sorted": {
                "lib": f"\"{os.path.abspath('source/runtime.c')}\"",
                "format": "sorted_val({0})",
                "type": "Value",
                "args": [{"name": "list", "type": "Value"}],
            },
            "set": {
                "lib": f"\"{os.path.abspath('source/runtime.c')}\"",
                "format": "set_val({0})",
                "type": "Value",
                "args": [{"name": "list", "type": "Value"}],
            }
        }

    def debug_log(self, kind, message):
        if self.debug:
            print(f"{'  ' * self.indent_level}[{kind}] {message}")

    @property
    def indent(self):
        return self.indent_str * self.indent_level

    def new_temp(self, prefix="_tmp", code=None):
        temp_hash = hashlib.md5(str(self.temp_num).encode()).hexdigest()[:8]
        self.temp_num += 1
        temp_name = f"{prefix}{temp_hash}"
        if code is not None:
            self.tmps[temp_name] = code
        return temp_name

    def visit(self, node):
        result = self.evaluate(node)
        if isinstance(result, dict) and result.get('stmt'):
            self.c_code.append(self.indent + result['code'])
        return result

    def evaluate(self, node):
        dispatch = {
            "Module": self.visit_module,
            "Assign": self.visit_assign,
            "Call": self.visit_call,
            "Name": self.visit_name,
            "Constant": self.visit_constant,
            "Expr": self.visit_expr,
            "List": self.visit_list,
            "Dict": self.visit_dict,
            "Tuple": self.visit_tuple,
            "FunctionDef": self.visit_function_def,
            "Return": self.visit_return,
            "BinOp": self.visit_binop,
            "JoinedStr": self.visit_joined_str,
            "FormattedValue": self.visit_formatted_value,
        }
        node_type = type(node).__name__
        if node_type in dispatch:
            return dispatch[node_type](node)
        else:
            raise NotImplementedError(f"Unsupported AST node type: {node_type}")

    def visit_formatted_value(self, node):
        # This visits the value inside the `{}` of an f-string
        value = self.visit(node.value)
        return {"code": f"to_string({value['code']})", "stmt": False}

    def visit_joined_str(self, node):
        if not f'#include "{os.path.abspath("source/ops.c")}"' in self.imports:
            self.imports.append(f'#include "{os.path.abspath("source/ops.c")}"')
        self.debug_log("JoinedStr", "Visiting joined string")

        parts = []
        for value in node.values:
            if isinstance(value, ast.Str):
                parts.append(f'create_string("{value.s}")')
            else:
                result = self.visit(value)
                if not result['stmt']:
                    parts.append(result['code'])
                else:
                    parts.append(result['code'] + ";")

        joined_str_code = f'join_strings({len(parts)}, {", ".join(parts)})'
        return {"code": joined_str_code, "stmt": False}

    def visit_function_def(self, node):
        self.debug_log("FunctionDef", f"Visiting function: {node.name}")

        func_name = node.name

        # Separate args
        args = [arg.arg for arg in node.args.args]
        defaults = node.args.defaults  # list of default values for last N args
        num_defaults = len(defaults)
        num_args = len(args)

        # Map args to defaults; defaults correspond to last N args
        default_map = {}
        for i, default_node in enumerate(defaults):
            arg_name = args[num_args - num_defaults + i]
            default_code = self.visit(default_node)["code"]
            default_map[arg_name] = default_code

        # *args and **kwargs
        vararg_name = node.args.vararg.arg if node.args.vararg else None
        kwarg_name = node.args.kwarg.arg if node.args.kwarg else None

        # Build function signature:
        # Use a generic 'Value' type for all params.
        # Required + optional args explicitly,
        # *args and **kwargs as 'Value *' or some generic struct pointer.
        params = []
        for i, arg in enumerate(args):
            params.append(f"Value {arg}")

        if vararg_name:
            params.append(f"Value *{vararg_name}")  # Or appropriate type for varargs
        if kwarg_name:
            params.append(f"Value {kwarg_name}")  # Or dict type for kwargs

        func_code_lines = [f"Value {func_name}({', '.join(params)}) {{"]

        # Insert code to assign defaults for optional args if they are some sentinel value.
        # (You’ll need some sentinel value, e.g. a special Value None or NULL to check)
        for arg in args:
            if arg in default_map:
                func_code_lines.append(
                    f"    if (is_none({arg})) {{ {arg} = {default_map[arg]}; }}"
                )

        # Append body statements
        for stmt in node.body:
            result = self.visit(stmt)
            if not result['stmt']:
                func_code_lines.append("    " + result['code'])
            else:
                func_code_lines.append("    " + result['code'] + ";")

        func_code_lines.append("}")

        func_code = "\n".join(func_code_lines)

        self.func_defs.append(func_code)
        self.functions[func_name] = {
            "name": func_name,
            "args": args,
            "defaults": default_map,
            "vararg": vararg_name,
            "kwarg": kwarg_name,
            "body": func_code_lines,
            "type": "Value",
        }

        return {"code": None, "stmt": False}

    def visit_return(self, node):
        self.debug_log("Return", "Visiting return statement")

        return_code = self.visit(node.value)['code']

        return {"code": f"return {return_code}", "stmt": True}

    def visit_binop(self, node):
        self.debug_log("BinOp", "Visiting binary operation")
        if not f'#include "{os.path.abspath("source/ops.c")}"' in self.imports:
            self.imports.append(f'#include "{os.path.abspath("source/ops.c")}"')

        left_code = self.visit(node.left)['code']
        right_code = self.visit(node.right)['code']
        op_class = node.op.__class__.__name__

        # Map Python AST operator classes to runtime C functions
        op_map = {
            "Add": "add_values",
            "Sub": "sub_values",
            "Mult": "mul_values",
            "Div": "div_values",
        }

        if op_class not in op_map:
            raise NotImplementedError(f"Unsupported binary operator: {op_class}")

        func = op_map[op_class]
        binop_code = f"{func}({left_code}, {right_code})"
        return {"code": binop_code, "stmt": False}

    def visit_tuple(self, node):
        self.debug_log("Tuple", "Visiting tuple")

        elements = []
        for element in node.elts:
            result = self.visit(element)
            if not result['stmt']:
                elements.append(result['code'])
            else:
                elements.append(result['code'] + ";")

        tmp_var = self.new_temp("_tuple_items", f"Value {{{{ temp_name }}}}[{len(elements)}] = {{{', '.join(elements)}}}")

        tuple_code = f"make_tuple({len(elements)}, {tmp_var})"
        return {"code": tuple_code, "stmt": False}

    def visit_list(self, node):
        self.debug_log("List", "Visiting list")

        tmp_items = []
        for i, item in enumerate(node.elts):
            item_code = self.visit(item)
            if not item_code['stmt']:
                tmp_items.append(item_code['code'])
            else:
                tmp_items.append(item_code['code'] + ";")

        tmp_var = self.new_temp("_list_items", f"Value {{{{ temp_name }}}}[{len(tmp_items)}] = {{{', '.join(tmp_items)}}}")

        list_code = f"make_list({len(tmp_items)}, {tmp_var})"
        return {"code": list_code, "stmt": False}

    def visit_dict(self, node):
        self.debug_log("Dict", "Visiting dictionary")

        key_exprs = []
        value_exprs = []

        for key, value in zip(node.keys, node.values):
            key_code = self.visit(key)
            value_code = self.visit(value)

            key_exprs.append(key_code['code'])
            value_exprs.append(value_code['code'])

        tmp_keys = self.new_temp("_dict_keys", f"Value {{{{ temp_name }}}}[{len(key_exprs)}] = {{{', '.join(key_exprs)}}}")
        tmp_values = self.new_temp("_dict_values", f"Value {{{{ temp_name }}}}[{len(value_exprs)}] = {{{', '.join(value_exprs)}}}")
        dict_code = f"make_dict({len(node.keys)}, {tmp_keys}, {tmp_values})"

        return {"code": dict_code, "stmt": False}

    def visit_module(self, node):
        self.debug_log("Module", "Visiting module")

        self.imports = [
            f'#include "{os.path.abspath("source/_global.c")}"',
            f'#include "{os.path.abspath("source/runtime.c")}"'
        ]

        self.func_defs.clear()
        body_code = []
        body_code.append(self.indent)

        body_code.append("int main() {")
        self.indent_level += 1

        body_code_tmp = []
        for stmt in node.body:
            result = self.visit(stmt)
            if result['code'] is None:
                continue
            if not result['stmt']:
                body_code_tmp.append(self.indent + result['code'])
            else:
                body_code_tmp.append(self.indent + result['code'] + ";")

        for tmp_name, tmp_code in self.tmps.items():
            body_code.append(f"{self.indent}{str(tmp_code).replace("{{ temp_name }}", str(tmp_name))};")

        if body_code_tmp and self.tmps:
            body_code.append(f"{self.indent}")
        self.tmps.clear()

        body_code.extend(body_code_tmp)

        free_code_lines = []
        for var_name, var_type in list(self.variables.items()):
            free_code_lines.append(f"{self.indent}free_value({var_name});")

        body_code.extend(free_code_lines)

        body_code.append(f"{self.indent}return 0;")
        self.indent_level -= 1
        body_code.append("}")

        self.c_code = self.imports + [self.indent] + self.func_defs + body_code

        return {"code": "\n".join(self.c_code), "stmt": False}

    def visit_assign(self, node):
        self.debug_log("Assign", "Visiting assignment")

        target = node.targets[0]
        target_name = target.id

        var_declared = target_name in self.variables
        value_node = self.visit(node.value)

        if isinstance(node.value, ast.Constant):
            val = node.value.value

            if isinstance(val, int):
                creation_code = f"create_int({val})"
                self.variables[target_name] = "TYPE_INT"
            elif isinstance(val, str):
                creation_code = f'create_string("{val}")'
                self.variables[target_name] = "TYPE_STRING"
            elif val is None:
                creation_code = "None"
                self.variables[target_name] = "TYPE_NONE"
            else:
                raise NotImplementedError(f"Unsupported constant type: {type(val)}")
        else:
            creation_code = value_node['code']

        if not var_declared:
            code = f"Value {target_name} = {creation_code}"
        else:
            code = f"{target_name} = {creation_code}"

        return {"code": code, "stmt": True}

    def visit_name(self, node):
        return {"code": node.id, "stmt": False}

    def visit_constant(self, node):
        val = node.value
        if isinstance(val, str):
            return {"code": f'create_string("{val}")', "stmt": False}
        elif isinstance(val, int):
            return {"code": f'create_int({val})', "stmt": False}
        elif val is None:
            return {"code": "None", "stmt": False}
        else:
            raise TypeError(f"Unsupported constant type: {type(val)}")

    def visit_expr(self, node):
        result = self.visit(node.value)
        if result.get('stmt'):
            return result
        else:
            return {"code": result['code'] + ";", "stmt": True}

    def visit_call(self, node):
        if not isinstance(node.func, ast.Name):
            raise NotImplementedError("Only direct function calls supported")

        func_name = node.func.id
        self.debug_log("Call", f"Visiting call: {func_name}")

        if func_name not in self.function_map and func_name not in self.functions:
            raise NameError(f"Function '{func_name}' not defined")

        if func_name in self.functions:
            func_def = self.functions[func_name]
            expected_arg_count = len(func_def['args'])
            defaults = func_def.get("defaults", {})

            evaluated_args = [self.visit(arg)['code'] for arg in node.args]
            actual_arg_count = len(evaluated_args)

            if actual_arg_count > expected_arg_count:
                raise Exception(f"Too many arguments for function '{func_name}'")

            # Fill in missing arguments with defaults if available
            if actual_arg_count < expected_arg_count:
                missing = expected_arg_count - actual_arg_count
                for i in range(missing):
                    arg_name = func_def['args'][actual_arg_count + i]
                    if arg_name not in defaults:
                        raise Exception(f"No default value for argument '{arg_name}' in function '{func_name}'")
                    evaluated_args.append(defaults[arg_name])

            code = f"{func_name}({', '.join(evaluated_args)})"
            return {"code": code, "stmt": False}

        # Handle function from function_map
        func_info = self.function_map[func_name]
        include_line = f'#include {func_info["lib"]}'
        if include_line not in self.imports:
            self.imports.append(include_line)

        # Visit all args to get their code
        provided_args = [self.visit(arg)['code'] for arg in node.args]
        expected_args = func_info["args"]

        final_args = []
        named_args = {}

        # Assign provided args to names
        for i, arg_def in enumerate(expected_args):
            if i < len(provided_args):
                val = provided_args[i]
                final_args.append(val)
                named_args[arg_def["name"]] = val
            else:
                final_args.append(None)  # placeholder for now

        # Now resolve missing args (defaults/code)
        for i, arg_def in enumerate(expected_args):
            if final_args[i] is not None:
                continue
            if "code" in arg_def:
                try:
                    val = eval(arg_def["code"], {}, named_args)
                except Exception as e:
                    raise ValueError(f"Error evaluating code for argument '{arg_def['name']}': {e}")
                final_args[i] = str(val)
                named_args[arg_def["name"]] = final_args[i]
            elif "default" in arg_def:
                final_args[i] = arg_def["default"]
                named_args[arg_def["name"]] = final_args[i]
            else:
                raise Exception(f"No value for argument '{arg_def['name']}' in function '{func_name}'")

        try:
            call_expr = func_info["format"].format(*final_args)
        except IndexError:
            raise ValueError(f"Insufficient arguments for function '{func_name}' formatting")

        return {"code": call_expr, "stmt": func_info["type"] == "void"}


