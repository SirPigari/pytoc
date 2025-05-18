#ifndef OPS_C
#define OPS_C

#include "runtime.c"
#include "_global.c"

#include <stdarg.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>


Value add_values(Value a, Value b) {
    if (a.type == TYPE_INT && b.type == TYPE_INT) {
        return create_int(a.int_val + b.int_val);
    } else {
        Value a_str = to_string(a);
        Value b_str = to_string(b);

        size_t len = strlen(a_str.string_val) + strlen(b_str.string_val);
        char* result = malloc(len + 1);
        if (!result) {
            fprintf(stderr, "add_values: memory allocation failed\n");
            exit(1);
        }
        strcpy(result, a_str.string_val);
        strcat(result, b_str.string_val);

        Value res = create_string(result);

        free(result);
        free(a_str.string_val);
        free(b_str.string_val);

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

Value join_strings(int count, ...) {
    va_list args;
    va_start(args, count);

    if (count == 0) {
        va_end(args);
        return create_string("");
    }

    // Temporary storage for arguments to calculate total length
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

#endif // OPS_C
