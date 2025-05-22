#ifndef GLOBAL_C
#define GLOBAL_C

#include "../headers/_global.h"

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

// Create int value
Value create_int(int val) {
    Value v;
    v.type = TYPE_INT;
    v.int_val = val;
    return v;
}

Value create_float(double val) {
    Value v;
    v.type = TYPE_FLOAT;
    v.float_val = val;
    return v;
}


Value create_bool(int b) {
    Value v;
    v.type = TYPE_BOOL;
    v.bool_val = b ? 1 : 0;
    return v;
}

// Create tuple value with size
Value create_tuple(int size) {
    Value v;
    v.type = TYPE_TUPLE;
    v.tuple_val.count = size;
    v.tuple_val.items = (Value*)malloc(sizeof(Value) * size);
    return v;
}

// Create list value with size
Value create_list(int size) {
    Value v;
    v.type = TYPE_LIST;
    v.list_val.count = size;
    v.list_val.items = (Value*)malloc(sizeof(Value) * size);
    return v;
}

// Create dict value with size
Value create_dict(int size) {
    Value v;
    v.type = TYPE_DICT;
    v.dict_val.count = size;
    v.dict_val.keys = (Value*)malloc(sizeof(Value) * size);
    v.dict_val.values = (Value*)malloc(sizeof(Value) * size);
    return v;
}

Value dict_set(Value* dict, Value key, Value value) {
    for (int i = 0; i < dict->dict_val.count; i++) {
        if (dict->dict_val.keys[i].type == TYPE_NONE) {
            dict->dict_val.keys[i] = key;
            dict->dict_val.values[i] = value;
            return None;
        }
    }
    fprintf(stderr, "Error: Dictionary is full\n");
    exit(1);
}


// Create set value with size
Value create_set(int size) {
    Value v;
    v.type = TYPE_SET;
    v.set_val.count = size;
    v.set_val.items = (Value*)malloc(sizeof(Value) * size);
    return v;
}

// Create frozen set value with size
Value create_frozenset(int size) {
    Value v;
    v.type = TYPE_FROZENSET;
    v.set_val.count = size;  // reuse set_val for frozenset
    v.set_val.items = (Value*)malloc(sizeof(Value) * size);
    return v;
}

// Create None value (singleton)
Value create_none() {
    Value v;
    v.type = TYPE_NONE;
    return v;
}

Value create_string(const char* str) {
    Value v;
    v.type = TYPE_STRING;
    if (!str) str = "";
    v.string_val = strdup(str);
    if (!v.string_val) {
        fprintf(stderr, "create_string: memory allocation failed\n");
        exit(1);
    }
    return v;
}

// Declare None singleton variable to be defined in C file
extern Value None;

// Print value recursively
void print_value(Value v) {
    switch (v.type) {
        case TYPE_NONE:
            printf("None");
            break;
        case TYPE_INT:
            printf("%d", v.int_val);
            break;
		case TYPE_FLOAT:
		    printf("%g", v.float_val);
		    break;
		case TYPE_BOOL:
		    printf("%s", v.bool_val ? "True" : "False");
		    break;
        case TYPE_TUPLE:
            printf("(");
            for (int i = 0; i < v.tuple_val.count; i++) {
                print_value(v.tuple_val.items[i]);
                if (i < v.tuple_val.count - 1) printf(", ");
            }
            printf(")");
            break;
        case TYPE_LIST:
            printf("[");
            for (int i = 0; i < v.list_val.count; i++) {
                print_value(v.list_val.items[i]);
                if (i < v.list_val.count - 1) printf(", ");
            }
            printf("]");
            break;
        case TYPE_DICT:
            printf("{");
            for (int i = 0; i < v.dict_val.count; i++) {
                print_value(v.dict_val.keys[i]);
                printf(": ");
                print_value(v.dict_val.values[i]);
                if (i < v.dict_val.count - 1) printf(", ");
            }
            printf("}");
            break;
        case TYPE_SET:
        case TYPE_FROZENSET:
            printf("{");
            for (int i = 0; i < v.set_val.count; i++) {
                print_value(v.set_val.items[i]);
                if (i < v.set_val.count - 1) printf(", ");
            }
            printf("}");
            break;
        case TYPE_STRING:
            printf("%s", v.string_val);
            break;
        default:
            printf("<unknown>");
            break;
    }
}

// Free memory recursively (for allocated items)
void free_value(Value v) {
    switch (v.type) {
        case TYPE_TUPLE:
            for (int i = 0; i < v.tuple_val.count; i++) {
                free_value(v.tuple_val.items[i]);
            }
            free(v.tuple_val.items);
            break;
        case TYPE_LIST:
            for (int i = 0; i < v.list_val.count; i++) {
                free_value(v.list_val.items[i]);
            }
            free(v.list_val.items);
            break;
        case TYPE_DICT:
            for (int i = 0; i < v.dict_val.count; i++) {
                free_value(v.dict_val.keys[i]);
                free_value(v.dict_val.values[i]);
            }
            free(v.dict_val.keys);
            free(v.dict_val.values);
            break;
        case TYPE_SET:
        case TYPE_FROZENSET:
            for (int i = 0; i < v.set_val.count; i++) {
                free_value(v.set_val.items[i]);
            }
            free(v.set_val.items);
            break;
        case TYPE_STRING:
            free(v.string_val);
            break;
        default:
            // Nothing to free for INT, NONE etc.
            break;
    }
}

char* str_concat(const char* a, const char* b) {
    size_t len_a = strlen(a);
    size_t len_b = strlen(b);
    char* result = malloc(len_a + len_b + 1);
    strcpy(result, a);
    strcat(result, b);
    return result;
}


Value copy_value(Value v) {
    Value copy;

    switch (v.type) {
        case TYPE_NONE:
            copy.type = TYPE_NONE;
            break;

        case TYPE_INT:
            copy.type = TYPE_INT;
            copy.int_val = v.int_val;
            break;

        case TYPE_STRING:
            copy.type = TYPE_STRING;
            copy.string_val = strdup(v.string_val ? v.string_val : "");
            if (!copy.string_val) {
                fprintf(stderr, "copy_value: memory allocation failed\n");
                exit(1);
            }
            break;

        case TYPE_TUPLE:
            copy.type = TYPE_TUPLE;
            copy.tuple_val.count = v.tuple_val.count;
            copy.tuple_val.items = malloc(sizeof(Value) * copy.tuple_val.count);
            if (!copy.tuple_val.items) {
                fprintf(stderr, "copy_value: memory allocation failed\n");
                exit(1);
            }
            for (int i = 0; i < copy.tuple_val.count; i++) {
                copy.tuple_val.items[i] = copy_value(v.tuple_val.items[i]);
            }
            break;

        case TYPE_LIST:
            copy.type = TYPE_LIST;
            copy.list_val.count = v.list_val.count;
            copy.list_val.items = malloc(sizeof(Value) * copy.list_val.count);
            if (!copy.list_val.items) {
                fprintf(stderr, "copy_value: memory allocation failed\n");
                exit(1);
            }
            for (int i = 0; i < copy.list_val.count; i++) {
                copy.list_val.items[i] = copy_value(v.list_val.items[i]);
            }
            break;

        case TYPE_DICT:
            copy.type = TYPE_DICT;
            copy.dict_val.count = v.dict_val.count;
            copy.dict_val.keys = malloc(sizeof(Value) * copy.dict_val.count);
            copy.dict_val.values = malloc(sizeof(Value) * copy.dict_val.count);
            if (!copy.dict_val.keys || !copy.dict_val.values) {
                fprintf(stderr, "copy_value: memory allocation failed\n");
                exit(1);
            }
            for (int i = 0; i < copy.dict_val.count; i++) {
                copy.dict_val.keys[i] = copy_value(v.dict_val.keys[i]);
                copy.dict_val.values[i] = copy_value(v.dict_val.values[i]);
            }
            break;

        case TYPE_SET:
        case TYPE_FROZENSET:
            copy.type = v.type; // same type (set or frozenset)
            copy.set_val.count = v.set_val.count;
            copy.set_val.items = malloc(sizeof(Value) * copy.set_val.count);
            if (!copy.set_val.items) {
                fprintf(stderr, "copy_value: memory allocation failed\n");
                exit(1);
            }
            for (int i = 0; i < copy.set_val.count; i++) {
                copy.set_val.items[i] = copy_value(v.set_val.items[i]);
            }
            break;

        default:
            fprintf(stderr, "copy_value: unsupported type %d\n", v.type);
            exit(1);
    }

    return copy;
}


#endif // GLOBAL_C
