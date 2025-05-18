#ifndef GLOBAL_H
#define GLOBAL_H

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

typedef enum {
    TYPE_NONE,    // Added None type
    TYPE_INT,
    TYPE_TUPLE,
    TYPE_STRING,
    TYPE_LIST,
    TYPE_DICT,
    TYPE_SET,
    TYPE_FROZENSET
} ValueType;

typedef struct Value Value;

typedef struct {
    int count;
    Value* items;
} Tuple;

typedef struct {
    int count;
    Value* items;
} List;

typedef struct {
    int count;
    Value* keys;
    Value* values;
} Dict;

typedef struct {
    int count;
    Value* items;
} Set;

struct Value {
    ValueType type;
    union {
        int int_val;
        char* string_val;
        Tuple tuple_val;
        List list_val;
        Dict dict_val;
        Set set_val;
    };
};

Value None = { .type = TYPE_NONE };

// Create int value
Value create_int(int val) {
    Value v;
    v.type = TYPE_INT;
    v.int_val = val;
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
    v.string_val = (char*)malloc(strlen(str) + 1);
    strcpy(v.string_val, str);
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
Value free_value(Value v) {
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
        default:
            break;
    }
    return None;
}

char* str_concat(const char* a, const char* b) {
    size_t len_a = strlen(a);
    size_t len_b = strlen(b);
    char* result = malloc(len_a + len_b + 1);
    strcpy(result, a);
    strcat(result, b);
    return result;
}

Value print(Value v) {
    print_value(v);
    printf("\n");
    fflush(stdout);
    return None;
}


#endif // GLOBAL_H
