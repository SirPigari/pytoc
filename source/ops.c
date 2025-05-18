#ifndef OPS_C
#define OPS_C

#include "runtime.c"
#include "_global.c"

Value add_values(Value a, Value b) {
    if (a.type == TYPE_INT && b.type == TYPE_INT) {
        return create_int(a.int_val + b.int_val);
    } else {
        // Coerce to string and concatenate
        Value a_str = to_string(a);
        Value b_str = to_string(b);
        size_t len = strlen(a_str.string_val) + strlen(b_str.string_val);
        char* result = malloc(len + 1);
        strcpy(result, a_str.string_val);
        strcat(result, b_str.string_val);
        Value res = create_string(result);
        free(result);
        return res;
    }
}


Value sub_values(Value a, Value b) {
    if (a.type == TYPE_INT && b.type == TYPE_INT) {
        return create_int(a.int_val - b.int_val);
    } else {
        fprintf(stderr, "TypeError: unsupported operand type(s) for -: '%s' and '%s'\n", type_name(a.type), type_name(b.type));
        exit(1);
    }
}

Value mul_values(Value a, Value b) {
    if (a.type == TYPE_INT && b.type == TYPE_INT) {
        return create_int(a.int_val * b.int_val);
    } else {
        fprintf(stderr, "TypeError: unsupported operand type(s) for *: '%s' and '%s'\n", type_name(a.type), type_name(b.type));
        exit(1);
    }
}

Value div_values(Value a, Value b) {
    if (a.type == TYPE_INT && b.type == TYPE_INT) {
        if (b.int_val == 0) {
            fprintf(stderr, "ZeroDivisionError: division by zero\n");
            exit(1);
        }
        return create_int(a.int_val / b.int_val);
    } else {
        fprintf(stderr, "TypeError: unsupported operand type(s) for /: '%s' and '%s'\n", type_name(a.type), type_name(b.type));
        exit(1);
    }
}

#endif OPS_C