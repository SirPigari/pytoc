#ifndef GLOBAL_H
#define GLOBAL_H

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

typedef enum {
    TYPE_NONE,
    TYPE_INT,
    TYPE_FLOAT,
    TYPE_TUPLE,
    TYPE_STRING,
    TYPE_LIST,
    TYPE_DICT,
    TYPE_SET,
    TYPE_FROZENSET,
    TYPE_BOOL
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

typedef struct {
    int count;
    Value* items;
} FrozenSet;

typedef struct {
    int bool_val;
} Bool;

typedef struct {
	double float_val;
} Float;

struct Value {
    ValueType type;
    union {
        int int_val;
        double float_val;
        char* string_val;
        int bool_val;
        Tuple tuple_val;
        List list_val;
        Dict dict_val;
        Set set_val;
    };
};

Value None = { .type = TYPE_NONE };
Value create_int(int val);
Value create_float(double val);
Value create_bool(int b);
Value create_tuple(int size);
Value create_list(int size);
Value create_dict(int size);
Value dict_set(Value* dict, Value key, Value value);
Value create_set(int size);
Value create_frozenset(int size);
Value create_none();
Value create_string(const char* str);
extern Value None;
void print_value(Value v);
void free_value(Value v);
char* str_concat(const char* a, const char* b);
Value print(Value v, Value sep_val, Value end_val);
Value copy_value(Value v);

#endif // GLOBAL_H
