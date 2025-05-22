#ifndef OPS_C
#define OPS_C

#include "../headers/ops.h"
#include "runtime.c"
#include "_global.c"
#include "exc.c"

#include <stdarg.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>  // For pow, floor, fmod, fabs
#include <ctype.h> // For isdigit

Value add_values(Value a, Value b) {
    if (a.type == TYPE_INT && b.type == TYPE_INT) {
        return create_int(a.int_val + b.int_val);
    } else if ((a.type == TYPE_FLOAT || a.type == TYPE_INT) &&
               (b.type == TYPE_FLOAT || b.type == TYPE_INT)) {
        double left = (a.type == TYPE_FLOAT) ? a.float_val : a.int_val;
        double right = (b.type == TYPE_FLOAT) ? b.float_val : b.int_val;
        return create_float(left + right);
    } else if (a.type == TYPE_STRING && b.type == TYPE_STRING) {
        return create_string(str_concat(a.string_val, b.string_val));
    } else if (a.type == TYPE_LIST && b.type == TYPE_LIST) {
        Value result = create_list(a.list_val.count + b.list_val.count);
        for (int i = 0; i < a.list_val.count; i++) {
            result.list_val.items[i] = copy_value(a.list_val.items[i]);
        }
        for (int i = 0; i < b.list_val.count; i++) {
            result.list_val.items[a.list_val.count + i] = copy_value(b.list_val.items[i]);
        }
        return result;
    } else if (a.type == TYPE_TUPLE && b.type == TYPE_TUPLE) {
        Value result = create_tuple(a.tuple_val.count + b.tuple_val.count);
        for (int i = 0; i < a.tuple_val.count; i++) {
            result.tuple_val.items[i] = copy_value(a.tuple_val.items[i]);
        }
        for (int i = 0; i < b.tuple_val.count; i++) {
            result.tuple_val.items[a.tuple_val.count + i] = copy_value(b.tuple_val.items[i]);
        }
        return result;
    } else {
        fprintf(stderr, "TypeError: unsupported operand type(s) for +: '%s' and '%s'\n",
                type_name(a.type), type_name(b.type));
        exit(1);
    }
}

Value sub_values(Value a, Value b) {
    if (a.type == TYPE_INT && b.type == TYPE_INT) {
        return create_int(a.int_val - b.int_val);
    } else if ((a.type == TYPE_FLOAT || a.type == TYPE_INT) &&
               (b.type == TYPE_FLOAT || b.type == TYPE_INT)) {
        double left = (a.type == TYPE_FLOAT) ? a.float_val : a.int_val;
        double right = (b.type == TYPE_FLOAT) ? b.float_val : b.int_val;
        return create_float(left - right);
    } else {
        fprintf(stderr, "TypeError: unsupported operand type(s) for -: '%s' and '%s'\n",
                type_name(a.type), type_name(b.type));
        exit(1);
    }
}

Value mul_values(Value a, Value b) {
    if (a.type == TYPE_INT && b.type == TYPE_INT) {
        return create_int(a.int_val * b.int_val);
    } else if ((a.type == TYPE_FLOAT || a.type == TYPE_INT) &&
               (b.type == TYPE_FLOAT || b.type == TYPE_INT)) {
        double left = (a.type == TYPE_FLOAT) ? a.float_val : a.int_val;
        double right = (b.type == TYPE_FLOAT) ? b.float_val : b.int_val;
        return create_float(left * right);
    } else if ((a.type == TYPE_STRING && b.type == TYPE_INT) || (a.type == TYPE_INT && b.type == TYPE_STRING)) {
        Value str_val = (a.type == TYPE_STRING) ? a : b;
        Value int_val = (a.type == TYPE_INT) ? a : b;
        int times = int_val.int_val;
        if (times < 0) times = 0;
        size_t len = strlen(str_val.string_val);
        char* buffer = malloc(times * len + 1);
        if (!buffer) exit(1);
        buffer[0] = '\0';
        for (int i = 0; i < times; i++) strcat(buffer, str_val.string_val);
        Value result = create_string(buffer);
        free(buffer);
        return result;
    } else if ((a.type == TYPE_LIST && b.type == TYPE_INT) || (a.type == TYPE_INT && b.type == TYPE_LIST)) {
        Value list_val = (a.type == TYPE_LIST) ? a : b;
        int times = (a.type == TYPE_INT) ? a.int_val : b.int_val;
        if (times < 0) times = 0;
        Value result = create_list(times * list_val.list_val.count);
        for (int i = 0; i < times; i++) {
            for (int j = 0; j < list_val.list_val.count; j++) {
                result.list_val.items[i * list_val.list_val.count + j] = copy_value(list_val.list_val.items[j]);
            }
        }
        return result;
    } else {
        fprintf(stderr, "TypeError: unsupported operand type(s) for *: '%s' and '%s'\n", type_name(a.type), type_name(b.type));
        exit(1);
    }
}

Value div_values(Value a, Value b) {
    if ((a.type == TYPE_FLOAT || a.type == TYPE_INT) &&
        (b.type == TYPE_FLOAT || b.type == TYPE_INT)) {
        double left = (a.type == TYPE_FLOAT) ? a.float_val : a.int_val;
        double right = (b.type == TYPE_FLOAT) ? b.float_val : b.int_val;
        if (fabs(right) < FLOAT_EPSILON) {
            fprintf(stderr, "ZeroDivisionError: division by zero\n");
            exit(1);
        }
        return create_float(left / right);
    } else {
        fprintf(stderr, "TypeError: unsupported operand type(s) for /: '%s' and '%s'\n", type_name(a.type), type_name(b.type));
        exit(1);
    }
}

Value pow_values(Value a, Value b) {
    if ((a.type == TYPE_FLOAT || a.type == TYPE_INT) &&
        (b.type == TYPE_FLOAT || b.type == TYPE_INT)) {
        double base = (a.type == TYPE_FLOAT) ? a.float_val : a.int_val;
        double exp  = (b.type == TYPE_FLOAT) ? b.float_val : b.int_val;
        return create_float(pow(base, exp));
    } else {
        fprintf(stderr, "TypeError: unsupported operand type(s) for **: '%s' and '%s'\n", type_name(a.type), type_name(b.type));
        exit(1);
    }
}

Value floordiv_values(Value a, Value b) {
    if ((a.type == TYPE_FLOAT || a.type == TYPE_INT) &&
        (b.type == TYPE_FLOAT || b.type == TYPE_INT)) {
        double left = (a.type == TYPE_FLOAT) ? a.float_val : a.int_val;
        double right = (b.type == TYPE_FLOAT) ? b.float_val : b.int_val;
        if (fabs(right) < FLOAT_EPSILON) {
            fprintf(stderr, "ZeroDivisionError: floor division by zero\n");
            exit(1);
        }
        return create_float(floor(left / right));
    } else {
        fprintf(stderr, "TypeError: unsupported operand type(s) for //: '%s' and '%s'\n", type_name(a.type), type_name(b.type));
        exit(1);
    }
}

Value mod_values(Value a, Value b) {
    if ((a.type == TYPE_FLOAT || a.type == TYPE_INT) &&
        (b.type == TYPE_FLOAT || b.type == TYPE_INT)) {
        double left = (a.type == TYPE_FLOAT) ? a.float_val : a.int_val;
        double right = (b.type == TYPE_FLOAT) ? b.float_val : b.int_val;
        if (fabs(right) < FLOAT_EPSILON) {
            fprintf(stderr, "ZeroDivisionError: modulo by zero\n");
            exit(1);
        }
        return create_float(fmod(left, right));
    } else {
        fprintf(stderr, "TypeError: unsupported operand type(s) for %%: '%s' and '%s'\n", type_name(a.type), type_name(b.type));
        exit(1);
    }
}

Value join_strings(int count, ...) {
    va_list args;
    va_start(args, count);

    if (count == 0) {
        va_end(args);
        return create_string("");
    }

    Value* vals = malloc(sizeof(Value) * count);
    if (!vals) {
        fprintf(stderr, "join_strings: memory allocation failed\n");
        exit(1);
    }

    size_t total_len = 0;
    for (int i = 0; i < count; i++) {
        vals[i] = va_arg(args, Value);
        if (vals[i].type != TYPE_STRING || vals[i].string_val == NULL) {
            fprintf(stderr, "join_strings: argument %d is not a valid string\n", i);
            free(vals);
            va_end(args);
            exit(1);
        }
        total_len += strlen(vals[i].string_val);
    }
    va_end(args);

    char* buffer = malloc(total_len + 1);
    if (!buffer) {
        fprintf(stderr, "join_strings: memory allocation failed\n");
        free(vals);
        exit(1);
    }
    buffer[0] = '\0';

    for (int i = 0; i < count; i++) {
        strcat(buffer, vals[i].string_val);
    }

    free(vals);

    Value result = create_string(buffer);
    free(buffer);
    return result;
}

// Comparisons

Value eq_values(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
            case TYPE_INT:
                return create_bool(a.int_val == b.int_val);
            case TYPE_FLOAT:
                return create_bool(fabs(a.float_val - b.float_val) < FLOAT_EPSILON);
            case TYPE_STRING:
                return create_bool(strcmp(a.string_val, b.string_val) == 0);
            case TYPE_BOOL:
                return create_bool(a.bool_val == b.bool_val);
            default:
                break;
        }
    }
    return create_bool(0);
}

Value ne_values(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
            case TYPE_INT:
                return create_bool(a.int_val != b.int_val);
            case TYPE_FLOAT:
                return create_bool(fabs(a.float_val - b.float_val) >= FLOAT_EPSILON);
            case TYPE_STRING:
                return create_bool(strcmp(a.string_val, b.string_val) != 0);
            case TYPE_BOOL:
                return create_bool(a.bool_val != b.bool_val);
            default:
                break;
        }
    }
    return create_bool(1);
}

Value lt_values(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
            case TYPE_INT:
                return create_bool(a.int_val < b.int_val);
            case TYPE_FLOAT:
                return create_bool(a.float_val < b.float_val - FLOAT_EPSILON);
            case TYPE_STRING:
                return create_bool(strcmp(a.string_val, b.string_val) < 0);
            case TYPE_BOOL:
                return create_bool(a.bool_val < b.bool_val);
            default:
                break;
        }
    }
    return create_bool(0);
}

Value le_values(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
            case TYPE_INT:
                return create_bool(a.int_val <= b.int_val);
            case TYPE_FLOAT:
                return create_bool(a.float_val < b.float_val + FLOAT_EPSILON);
            case TYPE_STRING:
                return create_bool(strcmp(a.string_val, b.string_val) <= 0);
            case TYPE_BOOL:
                return create_bool(a.bool_val <= b.bool_val);
            default:
                break;
        }
    }
    return create_bool(0);
}

Value gt_values(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
            case TYPE_INT:
                return create_bool(a.int_val > b.int_val);
            case TYPE_FLOAT:
                return create_bool(a.float_val > b.float_val + FLOAT_EPSILON);
            case TYPE_STRING:
                return create_bool(strcmp(a.string_val, b.string_val) > 0);
            case TYPE_BOOL:
                return create_bool(a.bool_val > b.bool_val);
            default:
                break;
        }
    }
    return create_bool(0);
}

Value ge_values(Value a, Value b) {
    if (a.type == b.type) {
        switch (a.type) {
            case TYPE_INT:
                return create_bool(a.int_val >= b.int_val);
            case TYPE_FLOAT:
                return create_bool(a.float_val > b.float_val - FLOAT_EPSILON);
            case TYPE_STRING:
                return create_bool(strcmp(a.string_val, b.string_val) >= 0);
            case TYPE_BOOL:
                return create_bool(a.bool_val >= b.bool_val);
            default:
                break;
        }
    }
    return create_bool(0);
}

// Unary operations
Value neg_values(Value a) {
	if (a.type == TYPE_INT) {
		return create_int(-a.int_val);
	} else if (a.type == TYPE_FLOAT) {
		return create_float(-a.float_val);
	} else {
		fprintf(stderr, "TypeError: unsupported operand type(s) for -: '%s'\n", type_name(a.type));
		exit(1);
	}
}

Value pos_values(Value a) {
	if (a.type == TYPE_INT) {
		return create_int(a.int_val);
	} else if (a.type == TYPE_FLOAT) {
		return create_float(a.float_val);
	} else {
		fprintf(stderr, "TypeError: unsupported operand type(s) for +: '%s'\n", type_name(a.type));
		exit(1);
	}
}

Value not_values(Value a) {
	if (a.type == TYPE_BOOL) {
		return create_bool(!a.bool_val);
	} else if (a.type == TYPE_INT) {
		return create_bool(a.int_val == 0);
	} else if (a.type == TYPE_FLOAT) {
		return create_bool(fabs(a.float_val) < FLOAT_EPSILON);
	} else if (a.type == TYPE_STRING) {
		return create_bool(strlen(a.string_val) == 0);
	} else {
		fprintf(stderr, "TypeError: unsupported operand type(s) for not: '%s'\n", type_name(a.type));
		exit(1);
	}
}

// Assert
Value assert(Value condition, Value message) {
	if (!condition.bool_val) {
		fprintf(stderr, "AssertionError: %s\n", message.string_val);
		exit(1);
	}
	return None;
}

#endif // OPS_C
