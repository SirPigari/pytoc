import ast
import os
import hashlib

class ScopedEnvironment:
    def __init__(self):
        self.stack = [{}]

    def enter(self):
        self.stack.append({})

    def exit(self):
        self.stack.pop()

    def set(self, name, value):
        self.stack[-1][name] = value

    def get(self, name):
        for scope in reversed(self.stack):
            if name in scope:
                return scope[name]
        return None  # Not found

    def current_scope(self):
        return self.stack[-1]


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
        self.inline_tmps = {}
        self.env = ScopedEnvironment()

        import os

        self.function_map = {
            "print": {
                "lib": f"\"{os.path.abspath('include/io.c')}\"",
                "format": "print({0}, {1}, {2})",
                "type": "Value",
                "args": [
                    {"name": "*args", "type": "Value", "default": "create_string(\"\")"},
                    {"name": "sep", "type": "Value", "default": "create_string(\" \")"},
                    {"name": "end", "type": "Value", "default": "create_string(\"\\n\")"},
                ]
            },
            "input": {
                "lib": f"\"{os.path.abspath('include/io.c')}\"",
                "format": "input({0})",
                "type": "Value",
                "args": [{"name": "prompt", "type": "Value", "default": "create_string(\"\")"}],
            },
            "int": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "to_int({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "str": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "to_string({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "float": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "to_float({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "list": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "to_list({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "len": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "len({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "abs": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "abs_val({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "max": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "max_val({0})",
                "type": "Value",
                "args": [{"name": "list", "type": "Value"}],
            },
            "min": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "min_val({0})",
                "type": "Value",
                "args": [{"name": "list", "type": "Value"}],
            },
            "sum": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "sum_val({0})",
                "type": "Value",
                "args": [{"name": "list", "type": "Value"}],
            },
            "bool": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "bool_val({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "ord": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "ord_val({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "chr": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "chr_val({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "range": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "range_val({0}, {1}, {2})",
                "type": "Value",
                "args": [
                    {"name": "start", "type": "int"},
                    {"name": "stop", "type": "int", "default": "None"},
                    {"name": "step", "type": "int", "default": "None"},
                ],
            },
            "range_start_stop": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "range_start_stop({0}, {1})",
                "type": "Value",
                "args": [{"name": "start", "type": "int"}, {"name": "stop", "type": "int"}],
            },
            "reversed": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "reversed_val({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "upper": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "upper_val({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "lower": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "lower_val({0})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}],
            },
            "isinstance": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "isinstance_val({0}, {1})",
                "type": "Value",
                "args": [{"name": "v", "type": "Value"}, {"name": "type", "type": "ValueType"}],
            },
            "sorted": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "sorted_val({0})",
                "type": "Value",
                "args": [{"name": "list", "type": "Value"}],
            },
            "set": {
                "lib": f"\"{os.path.abspath('include/runtime.c')}\"",
                "format": "set_val({0})",
                "type": "Value",
                "args": [{"name": "list", "type": "Value"}],
            }
        }

    def debug_log(self, kind, message):
        if self.debug:
            print(f"{self.indent_str * self.indent_level}[{kind}] {message}")

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

    def _unique_label(self, prefix="label"):
        if not hasattr(self, "_label_counter"):
            self.temp_num = 0
        label = f"{prefix}_{self.temp_num}"
        self.temp_num += 1
        return label

    def new_temp_inplace(self, prefix="_tmp", code=None):
        temp_hash = hashlib.md5(str(self.temp_num).encode()).hexdigest()[:8]
        self.temp_num += 1
        temp_name = f"{prefix}{temp_hash}"
        if code is not None:
            self.inline_tmps[temp_name] = code
        return temp_name.replace("{{ temp_name }}", temp_name)

    def visit(self, node):
        result = self.evaluate(node)
        if isinstance(result, dict) and result.get('stmt'):
            self.c_code.append(self.indent + result['code'])
        return result

    def evaluate(self, node):
        dispatch = {
            "Module": self.visit_module,
            "Assign": self.visit_assign,
            "AugAssign": self.visit_aug_assign,
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
            "For": self.visit_for,
            "While": self.visit_while,
            "Compare": self.visit_compare,
            "Assert": self.visit_assert,
            "UnaryOp": self.visit_unary_op,
            "Try": self.visit_try,
            "ExceptHandler": self.visit_except_handler,
            "Pass": lambda node: {"code": "", "stmt": False},
            "Raise": self.visit_raise,
        }
        node_type = type(node).__name__
        if node_type in dispatch:
            return dispatch[node_type](node)
        else:
            raise NotImplementedError(f"Unsupported AST node type: {node_type}")

    def visit_raise(self, node):
        if not f'#include "{os.path.abspath("include/exc.c")}"' in self.imports:
            self.imports.append(f'#include "{os.path.abspath("include/exc.c")}"')

        self.debug_log("Raise", "Visiting raise statement")
        exc_type = node.exc
        exc_code = self.visit(exc_type)
        raise_code = f"raise_exception({exc_type}, {exc_code['code']})"
        return {"code": raise_code, "stmt": True}

    def visit_except_handler(self, node):
        self.debug_log("ExceptHandler", "Visiting except handler")

        # Create a new temporary variable for the exception
        exc_var = self.new_temp("_exc")
        self.variables[exc_var] = "Value"

        # Generate code for the exception handler
        handler_code = []
        if node.type:
            type_code = self.visit(node.type)['code']
            handler_code.append(f"if (isinstance({exc_var}, {type_code})) {{")
        else:
            handler_code.append("{")

        self.indent_level += 1
        for stmt in node.body:
            result = self.visit(stmt)
            if result['stmt']:
                handler_code.append(self.indent + result['code'] + ";")
            else:
                handler_code.append(self.indent + result['code'])
        self.indent_level -= 1

        handler_code.append(f"{self.indent}}}")

        return {"code": "\n".join(handler_code), "stmt": True}

    def visit_try(self, node):
        self.debug_log("Try", "Visiting try block")

        try_catch_include = f'#include "{os.path.abspath("include/try-catch.c")}"'
        if try_catch_include not in self.imports:
            self.imports.append(try_catch_include)
        exc_include = f'#include "{os.path.abspath("include/exc.c")}"'
        if exc_include not in self.imports:
            self.imports.append(exc_include)

        ctx_name = self.new_temp(prefix="_ctx")
        exc_name = self.new_temp(prefix="_exc")
        exc_name_2 = self.new_temp("_exc")

        declaration = f"TryCatchContext {ctx_name};"
        exc_declaration = f"Exception {exc_name};"
        self.indent_level -= 1
        declaration_2 = f"{self.indent}TryCatchContext *{exc_name_2};"
        try_header = f"{self.indent}TRY(&{ctx_name}) {{"
        catch_header = f"{self.indent}}} CATCH(&{ctx_name}, {exc_name}) {{"
        try_ending = f"{self.indent}}} END_TRY(&{ctx_name})"

        # Generate TRY body
        self.indent_level += 1
        try_code = []
        for stmt in node.body:
            result = self.visit(stmt)
            code_line = self.indent + result['code']
            if result['stmt']:
                code_line += ";"
            try_code.append(code_line)
        self.indent_level -= 1

        self.indent_level += 1
        except_code = []

        for handler in node.handlers:
            if handler.type is not None and hasattr(handler.type, 'id'):
                exception_type = handler.type.id
            else:
                exception_type = "Exception"

            # NOTE: `_exc` is a C-side variable you must define in your runtime
            except_code.append(f"{self.indent}Value {exc_name} = make_value_from_exc({exc_name_2});")
            check_line = f"{self.indent}if (is_true(isinstance(&{exc_name}, &{exception_type}))) {{"
            except_code.append(check_line)
            old_temps_inplace = self.inline_tmps
            self.indent_level += 1
            for stmt in handler.body:
                self.inline_tmps.clear()
                result = self.visit(stmt)
                if self.inline_tmps:
                    self.debug_log("InlineTmps", f"Inlined temporary variables: {self.inline_tmps}")
                for tmp_name, tmp_code in self.inline_tmps.items():
                    line = f"{self.indent}{str(tmp_code).replace('{{ temp_name }}', str(tmp_name))};"
                    except_code.append(line)
                line = self.indent + result['code']
                if result['stmt']:
                    line += ";"
                except_code.append(line)
            self.indent_level -= 1
            except_code.append(self.indent + "}")

        # Restore the original inline temporary variables
        self.inline_tmps = old_temps_inplace
        self.indent_level -= 1

        full_code = "\n".join([
            declaration,
            declaration_2,
            try_header,
            *try_code,
            catch_header,
            *except_code,
            try_ending,
        ])

        return {"code": full_code, "stmt": True}

    def visit_unary_op(self, node):
        self.debug_log("UnaryOp", "Visiting unary operation")
        if not f'#include "{os.path.abspath("include/ops.c")}"' in self.imports:
            self.imports.append(f'#include "{os.path.abspath("include/ops.c")}"')

        operand_code = self.visit(node.operand)['code']
        op_class = node.op.__class__.__name__

        # Map Python AST operator classes to runtime C functions
        op_map = {
            "Not": "not_values",
            "USub": "neg_values",
            "UAdd": "pos_values",
        }

        if op_class not in op_map:
            raise NotImplementedError(f"Unsupported unary operator: {op_class}")

        func = op_map[op_class]
        unary_code = f"{func}({operand_code})"
        return {"code": unary_code, "stmt": False}

    def visit_assert(self, node):
        self.debug_log("Assert", "Visiting assert statement")
        if not f'#include "{os.path.abspath("include/ops.c")}"' in self.imports:
            self.imports.append(f'#include "{os.path.abspath("include/ops.c")}"')

        condition_code = self.visit(node.test)['code']
        message_code = self.visit(node.msg)['code'] if node.msg else 'None'

        assert_code = f"assert({condition_code}, {message_code})"
        return {"code": assert_code, "stmt": True}

    def visit_compare(self, node):
        self.debug_log("Compare", "Visiting comparison")
        if not f'#include "{os.path.abspath("include/ops.c")}"' in self.imports:
            self.imports.append(f'#include "{os.path.abspath("include/ops.c")}"')

        left_code = self.visit(node.left)['code']
        op_code = node.ops[0].__class__.__name__
        right_code = self.visit(node.comparators[0])['code']

        # Map Python AST operator classes to runtime C functions
        op_map = {
            "Eq": "eq_values",
            "NotEq": "ne_values",
            "Lt": "lt_values",
            "LtE": "le_values",
            "Gt": "gt_values",
            "GtE": "ge_values",
        }

        if op_code not in op_map:
            raise NotImplementedError(f"Unsupported comparison operator: {op_code}")

        func = op_map[op_code]
        compare_code = f"{func}({left_code}, {right_code})"
        return {"code": compare_code, "stmt": False}

    def visit_while(self, node):
        self.debug_log("While", "Visiting while loop")

        condition_code = self.visit(node.test)['code']
        loop_body = []

        self.indent_level += 1
        for stmt in node.body:
            result = self.visit(stmt)
            if result['stmt']:
                loop_body.append(self.indent + result['code'] + ";")
            else:
                loop_body.append(self.indent + result['code'])

        self.indent_level -= 1

        loop_code = f"{self.indent}while (is_true({condition_code})) {{\n"
        loop_code += "\n".join(loop_body)
        loop_code += f"\n{self.indent}}}"

        return {"code": loop_code, "stmt": True}

    def visit_aug_assign(self, node):
        self.debug_log("AugAssign", "Visiting augmented assignment")
        if not f'#include "{os.path.abspath("include/ops.c")}"' in self.imports:
            self.imports.append(f'#include "{os.path.abspath("include/ops.c")}"')

        target = node.target
        target_name = target.id
        op = node.op.__class__.__name__

        # Map Python AST operator classes to runtime C functions
        op_map = {
            "Add": "add_values",
            "Sub": "sub_values",
            "Mult": "mul_values",
            "Div": "div_values",
        }

        if op not in op_map:
            raise NotImplementedError(f"Unsupported augmented assignment operator: {op}")

        func = op_map[op]
        value_code = self.visit(node.value)['code']
        code = f"{target_name} = {func}({target_name}, {value_code})"

        return {"code": code, "stmt": True}

    def visit_for(self, node):
        self.debug_log("For", "Visiting for loop")

        loop_var = node.target.id
        iter_expr = self.visit(node.iter)
        iter_code = iter_expr['code']

        iter_tmp = self.new_temp("_iter")
        index_var = self.new_temp("_index")

        # Save the iterable in a temporary variable
        init_iter = f"Value {iter_tmp} = {iter_code};"
        loop_header = f"{self.indent}for (int {index_var} = 0; {index_var} < {iter_tmp}.list_val.count; {index_var}++) {{"

        self.indent_level += 1
        loop_body = [f"{self.indent}Value {loop_var} = {iter_tmp}.list_val.items[{index_var}];"]

        inline_tmps = self.inline_tmps

        for stmt in node.body:
            self.inline_tmps.clear()
            result = self.visit(stmt)
            if self.inline_tmps:
                self.debug_log("InlineTmps", f"Inlined temporary variables: {self.inline_tmps}")
            for tmp_name, tmp_code in self.inline_tmps.items():
                loop_body.append(f"{self.indent}{str(tmp_code).replace('{{ temp_name }}', str(tmp_name))};")
            if result['stmt']:
                if result['code'].endswith(";"):
                    loop_body.append(self.indent + result['code'])
                else:
                    loop_body.append(self.indent + result['code'] + ";")
            else:
                loop_body.append(self.indent + result['code'])

        self.inline_tmps.clear()
        self.inline_tmps = inline_tmps

        self.indent_level -= 1
        loop_footer = f"{self.indent}}}"

        full_loop = '\n'.join([init_iter, loop_header] + loop_body + [loop_footer])
        return {"code": full_loop, "stmt": True}

    def visit_formatted_value(self, node):
        # This visits the value inside the `{}` of an f-string
        value = self.visit(node.value)
        return {"code": f"to_string({value['code']})", "stmt": False}

    def visit_joined_str(self, node):
        if not f'#include "{os.path.abspath("include/ops.c")}"' in self.imports:
            self.imports.append(f'#include "{os.path.abspath("include/ops.c")}"')
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
        if func_name == "main":
            func_name = self.new_temp("_main")

        # Extract argument names and defaults
        args = [arg.arg for arg in node.args.args]
        defaults = node.args.defaults
        num_defaults = len(defaults)
        num_args = len(args)

        # Map default values
        default_map = {}
        for i, default_node in enumerate(defaults):
            arg_name = args[num_args - num_defaults + i]
            default_code = self.visit(default_node)["code"]
            default_map[arg_name] = default_code

        vararg_name = node.args.vararg.arg if node.args.vararg else None
        kwarg_name = node.args.kwarg.arg if node.args.kwarg else None

        # Function signature in C
        params = [f"Value {arg}" for arg in args]
        if vararg_name:
            params.append(f"Value *{vararg_name}")
        if kwarg_name:
            params.append(f"Value {kwarg_name}")

        func_code_lines = [f"Value {func_name}({', '.join(params)}) {{"]

        # Handle default values in body
        for arg in args:
            if arg in default_map:
                func_code_lines.append(
                    f"    if (is_none({arg})) {{ {arg} = {default_map[arg]}; }}"
                )

        # Spawn a new transpiler with its own scope
        function_transpiler = PYTOCTranspiler(debug=self.debug)
        function_transpiler.indent_level = self.indent_level + 1

        # Shared state if needed
        function_transpiler.imports = self.imports
        function_transpiler.func_defs = self.func_defs
        function_transpiler.constants = self.constants
        function_transpiler.functions = self.functions

        # Setup a new scope
        function_transpiler.env = ScopedEnvironment()
        function_transpiler.env.enter()

        for arg in args:
            function_transpiler.env.set(arg, "Value")
        if vararg_name:
            function_transpiler.env.set(vararg_name, "Value*")
        if kwarg_name:
            function_transpiler.env.set(kwarg_name, "Value")

        # Visit function body
        for stmt in node.body:
            result = function_transpiler.visit(stmt)

            if function_transpiler.inline_tmps:
                function_transpiler.debug_log("InlineTmps",
                                              f"Inlined temporary variables: {function_transpiler.inline_tmps}")
            for tmp_name, tmp_code in function_transpiler.inline_tmps.items():
                func_code_lines.append(
                    "    " + tmp_code.replace("{{ temp_name }}", tmp_name) + ";"
                )
            function_transpiler.inline_tmps.clear()

            if result['code'] is None:
                continue
            if not result['stmt']:
                func_code_lines.append("    " + result['code'])
            else:
                func_code_lines.append("    " + result['code'] + ";")

        # End of function
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
        if not f'#include "{os.path.abspath("include/ops.c")}"' in self.imports:
            self.imports.append(f'#include "{os.path.abspath("include/ops.c")}"')

        left_code = self.visit(node.left)['code']
        right_code = self.visit(node.right)['code']
        op_class = node.op.__class__.__name__

        # Map Python AST operator classes to runtime C functions
        op_map = {
            "Add": "add_values",
            "Sub": "sub_values",
            "Mult": "mul_values",
            "Div": "div_values",
            "Mod": "mod_values",
            "FloorDiv": "floordiv_values",
            "Pow": "pow_values",
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

        tmp_var = self.new_temp_inplace("_tuple_items", f"Value {{{{ temp_name }}}}[{len(elements)}] = {{{', '.join(elements)}}}")

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

        tmp_var = self.new_temp_inplace("_list_items", f"Value {{{{ temp_name }}}}[{len(tmp_items)}] = {{{', '.join(tmp_items)}}}")

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

        tmp_keys = self.new_temp_inplace("_dict_keys", f"Value {{{{ temp_name }}}}[{len(key_exprs)}] = {{{', '.join(key_exprs)}}}")
        tmp_values = self.new_temp_inplace("_dict_values", f"Value {{{{ temp_name }}}}[{len(value_exprs)}] = {{{', '.join(value_exprs)}}}")
        dict_code = f"make_dict({len(node.keys)}, {tmp_keys}, {tmp_values})"

        return {"code": dict_code, "stmt": False}

    def visit_module(self, node):
        self.debug_log("Module", "Visiting module")

        self.imports = [
            f'#include "{os.path.abspath("include/_global.c")}"',
            f'#include "{os.path.abspath("include/runtime.c")}"',
        ]

        self.func_defs.clear()
        body_code = []
        body_code.append(self.indent)

        body_code.append("int main() {")
        self.indent_level += 1

        body_code_tmp = []
        for stmt in node.body:
            result = self.visit(stmt)
            if self.inline_tmps:
                self.debug_log("InlineTmps", f"Inlined temporary variables: {self.inline_tmps}")
            for tmp_name, tmp_code in self.inline_tmps.items():
                body_code_tmp.append(f"{self.indent}{str(tmp_code).replace('{{ temp_name }}', str(tmp_name))};")
            self.inline_tmps.clear()
            if result['code'] is None:
                continue
            if not result['stmt']:
                body_code_tmp.append(self.indent + result['code'])
            else:
                body_code_tmp.append(self.indent + result['code'] + ";")

        for tmp_name, tmp_code in self.tmps.items():
            body_code.append(f"{self.indent}{str(tmp_code).replace("{{ temp_name }}", str(tmp_name))};")


        inits = []
        if f'#include "{os.path.abspath("include/exc.c")}"' in self.imports:
            print("Include exc.c")
            inits.append(f"{self.indent}init_exc();")

        if inits:
            for init in inits:
                body_code.append(init)
            body_code.append(f"{self.indent}")

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

        body_code.append(f"{self.indent}")

        message = [
            "// ---------------------------------- //",
            "//     Generated by PYTOCTranspiler   //",
            "//            By SirPigari            //",
            "// https://github.com/SirPigari/pytoc //",
            "// ---------------------------------- //",
            "",
        ]

        self.c_code = self.imports + [self.indent] + message + self.func_defs + body_code

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
            elif isinstance(val, float):
                creation_code = f"create_float({val})"
                self.variables[target_name] = "TYPE_FLOAT"
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
        elif val is None:
            return {"code": "None", "stmt": False}
        elif isinstance(val, bool):
            value = 0 if not val else 1
            return {"code": f'create_bool({value})', "stmt": False}
        elif isinstance(val, int):
            return {"code": f'create_int({val})', "stmt": False}
        elif isinstance(val, float):
            return {"code": f'create_float({val})', "stmt": False}
        else:
            raise TypeError(f"Unsupported constant type: {type(val)}")

    def visit_expr(self, node):
        result = self.visit(node.value)
        if result.get('stmt'):
            return {"code": result['code'] + ";", "stmt": True}
        else:
            return {"code": result['code'], "stmt": True}

    def visit_call(self, node):
        if not isinstance(node.func, ast.Name):
            raise NotImplementedError("Only direct function calls supported")

        func_name = node.func.id
        if func_name == "main":
            for t in self.functions.keys():
                if t.startswith("_main"):
                    func_name = t
                    break

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

        func_info = self.function_map[func_name]
        expected_args = func_info["args"]

        include_lib = f"#include {func_info['lib']}"
        if include_lib not in self.imports:
            self.imports.append(include_lib)

        # Detect *args
        star_arg_index = -1
        arg_names = []
        for i, arg in enumerate(expected_args):
            name = arg["name"]
            if name.startswith("**"):
                raise NotImplementedError("**kwargs not supported yet")
            if name.startswith("*"):
                if star_arg_index != -1:
                    raise SyntaxError(f"Multiple starred args not allowed: {name}")
                star_arg_index = i
            arg_names.append(name.lstrip("*"))

        # Visit all arguments
        pos_args = []
        kw_args = {}
        for arg in node.args:
            pos_args.append(self.visit(arg)["code"])
        for kw in node.keywords:
            if kw.arg is None:
                raise NotImplementedError("**kwargs not supported yet")
            kw_args[kw.arg] = self.visit(kw.value)["code"]

        final_args = []
        named_args = {}

        if star_arg_index != -1:
            num_pos = star_arg_index
            if len(pos_args) < num_pos:
                raise Exception(f"Missing positional arguments for function '{func_name}'")

            # Pre-*args
            final_args.extend(pos_args[:num_pos])
            for i in range(num_pos):
                named_args[arg_names[i]] = pos_args[i]

            # Handle *args group as a temporary array
            starred_items = pos_args[num_pos:]
            array_init = ", ".join(starred_items)
            array_len = len(starred_items)

            temp_name = self.new_temp_inplace(
                prefix=f"_{func_name}_args",
                code=f"Value {{{{ temp_name }}}}[{array_len}] = {{ {array_init} }}"
            )
            star_val = f"make_list({array_len}, {temp_name})"

            final_args.append(star_val)
            named_args[arg_names[star_arg_index]] = star_val

            # Handle keyword/named args after *args
            for i in range(star_arg_index + 1, len(expected_args)):
                arg_def = expected_args[i]
                name = arg_def["name"]
                bare_name = name.lstrip("*")
                if bare_name in kw_args:
                    val = kw_args[bare_name]
                elif "code" in arg_def:
                    val = eval(arg_def["code"], {}, named_args)
                elif "default" in arg_def:
                    val = arg_def["default"]
                else:
                    raise Exception(f"No value for argument '{bare_name}'")
                final_args.append(val)
                named_args[bare_name] = val
        else:
            # No *args
            for i, arg_def in enumerate(expected_args):
                name = arg_def["name"]
                bare_name = name.lstrip("*")
                if i < len(pos_args):
                    val = pos_args[i]
                elif bare_name in kw_args:
                    val = kw_args[bare_name]
                elif "code" in arg_def:
                    val = eval(arg_def["code"], {}, named_args)
                elif "default" in arg_def:
                    val = arg_def["default"]
                else:
                    raise Exception(f"No value for argument '{bare_name}'")
                final_args.append(val)
                named_args[bare_name] = val

        try:
            call_expr = func_info["format"].format(*final_args)
        except IndexError:
            raise ValueError(f"Insufficient arguments for function '{func_name}' formatting")

        return {"code": call_expr, "stmt": func_info["type"] == "void"}


