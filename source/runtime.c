#ifndef RUNTIME_C
#define RUNTIME_C

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdbool.h>
#include "_global.c"

const char* type_name(ValueType t) {
    switch (t) {
        case TYPE_NONE: return "NoneType";
        case TYPE_INT: return "int";
        case TYPE_STRING: return "str";
        case TYPE_LIST: return "list";
        case TYPE_TUPLE: return "tuple";
        case TYPE_DICT: return "dict";
        case TYPE_SET: return "set";
        case TYPE_FROZENSET: return "frozenset";
        default: return "unknown";
    }
}


// Convert a Value to an integer
Value to_int(Value v) {
    switch (v.type) {
        case TYPE_INT:
            return v;
        case TYPE_STRING:
            return create_int(atoi(v.string_val));  // basic string to int
        default:
            fprintf(stderr, "TypeError: cannot convert to int\n");
            exit(1);
    }
}

Value to_string(Value v) {
    char buffer[64];
    switch (v.type) {
        case TYPE_INT:
            snprintf(buffer, sizeof(buffer), "%d", v.int_val);
            return create_string(buffer);
        case TYPE_STRING:
            return v;
        case TYPE_NONE:
            return create_string("None");
        case TYPE_LIST:
        case TYPE_TUPLE:
            snprintf(buffer, sizeof(buffer), "<%s object>", type_name(v.type));
            return create_string(buffer);
        case TYPE_DICT:
            snprintf(buffer, sizeof(buffer), "<%s object>", type_name(v.type));
            return create_string(buffer);
        case TYPE_SET:
        case TYPE_FROZENSET:
            snprintf(buffer, sizeof(buffer), "<%s object>", type_name(v.type));
            return create_string(buffer);
        default:
            fprintf(stderr, "TypeError: cannot convert to str\n");
            exit(1);
    }
}

Value len(Value v) {
    switch (v.type) {
        case TYPE_STRING:
            return create_int(strlen(v.string_val));
        case TYPE_LIST:
            return create_int(v.list_val.count);
        case TYPE_TUPLE:
            return create_int(v.tuple_val.count);
        case TYPE_DICT:
            return create_int(v.dict_val.count);
        case TYPE_SET:
        case TYPE_FROZENSET:
            return create_int(v.set_val.count);
        case TYPE_NONE:
            return create_int(0);
        case TYPE_INT: {
            int n = abs(v.int_val);
            int count = (n == 0) ? 1 : 0;
            while (n > 0) {
                count++;
                n /= 10;
            }
            return create_int(count);
        }
        default:
            fprintf(stderr, "TypeError: object of type '%s' has no len()\n", type_name(v.type));
            exit(1);
    }
}

Value abs_val(Value v) {
    if (v.type != TYPE_INT) {
        fprintf(stderr, "TypeError: bad operand type for abs()\n");
        exit(1);
    }
    return create_int(abs(v.int_val));
}

Value max_val(Value list) {
    if (list.type != TYPE_LIST || list.list_val.count == 0) {
        fprintf(stderr, "TypeError: max() arg is empty or not a list\n");
        exit(1);
    }
    Value max = list.list_val.items[0];
    for (int i = 1; i < list.list_val.count; i++) {
        if (list.list_val.items[i].type == TYPE_INT && max.type == TYPE_INT) {
            if (list.list_val.items[i].int_val > max.int_val) {
                max = list.list_val.items[i];
            }
        } else {
            fprintf(stderr, "TypeError: max() supports only ints in list\n");
            exit(1);
        }
    }
    return max;
}

Value min_val(Value list) {
    if (list.type != TYPE_LIST || list.list_val.count == 0) {
        fprintf(stderr, "TypeError: min() arg is empty or not a list\n");
        exit(1);
    }
    Value min = list.list_val.items[0];
    for (int i = 1; i < list.list_val.count; i++) {
        if (list.list_val.items[i].type == TYPE_INT && min.type == TYPE_INT) {
            if (list.list_val.items[i].int_val < min.int_val) {
                min = list.list_val.items[i];
            }
        } else {
            fprintf(stderr, "TypeError: min() supports only ints in list\n");
            exit(1);
        }
    }
    return min;
}

Value sum_val(Value list) {
    if (list.type != TYPE_LIST) {
        fprintf(stderr, "TypeError: sum() expects a list\n");
        exit(1);
    }
    int total = 0;
    for (int i = 0; i < list.list_val.count; i++) {
        if (list.list_val.items[i].type != TYPE_INT) {
            fprintf(stderr, "TypeError: sum() supports only ints\n");
            exit(1);
        }
        total += list.list_val.items[i].int_val;
    }
    return create_int(total);
}

Value bool_val(Value v) {
    int truth = 0;
    switch (v.type) {
        case TYPE_NONE:
            truth = 0;
            break;
        case TYPE_INT:
            truth = (v.int_val != 0);
            break;
        case TYPE_STRING:
            truth = (strlen(v.string_val) != 0);
            break;
        case TYPE_LIST:
            truth = (v.list_val.count != 0);
            break;
        case TYPE_TUPLE:
            truth = (v.tuple_val.count != 0);
            break;
        case TYPE_DICT:
            truth = (v.dict_val.count != 0);
            break;
        case TYPE_SET:
        case TYPE_FROZENSET:
            truth = (v.set_val.count != 0);
            break;
        default:
            truth = 1;
    }
    return create_int(truth);
}

// ord() - get int ordinal of single char string
Value ord_val(Value v) {
    if (v.type != TYPE_STRING || strlen(v.string_val) != 1) {
        fprintf(stderr, "TypeError: ord() expected a single character string\n");
        exit(1);
    }
    return create_int((int)v.string_val[0]);
}

// chr() - get char string from int ordinal
Value chr_val(Value v) {
    if (v.type != TYPE_INT || v.int_val < 0 || v.int_val > 255) {
        fprintf(stderr, "ValueError: chr() arg out of range\n");
        exit(1);
    }
    char buffer[2] = { (char)v.int_val, '\0' };
    return create_string(buffer);
}

// range() - simplified, creates list of ints from start to end-1
Value range_val(int start, int stop, int step) {
    if (step == 0) {
        fprintf(stderr, "ValueError: range() step argument must not be zero\n");
        exit(1);
    }
    int count = 0;
    if ((step > 0 && start >= stop) || (step < 0 && start <= stop)) {
        return create_list(0); // empty list
    }
    for (int i = start; (step > 0) ? (i < stop) : (i > stop); i += step) {
        count++;
    }
    Value list = create_list(count);
    int index = 0;
    for (int i = start; (step > 0) ? (i < stop) : (i > stop); i += step) {
        list.list_val.items[index++] = create_int(i);
    }
    return list;
}

// Overloads for range_val with 1 or 2 arguments
Value range_stop(int stop) {
    return range_val(0, stop, 1);
}

Value range_start_stop(int start, int stop) {
    return range_val(start, stop, 1);
}

// reversed() - returns a reversed list copy
Value reversed_val(Value v) {
    if (v.type != TYPE_LIST) {
        fprintf(stderr, "TypeError: reversed() expects a list\n");
        exit(1);
    }
    Value rev = create_list(v.list_val.count);
    for (int i = 0; i < v.list_val.count; i++) {
        rev.list_val.items[i] = v.list_val.items[v.list_val.count - 1 - i];
    }
    return rev;
}

// upper() for strings
Value upper_val(Value v) {
    if (v.type != TYPE_STRING) {
        fprintf(stderr, "TypeError: upper() expects a string\n");
        exit(1);
    }
    int len = strlen(v.string_val);
    char* buffer = (char*)malloc(len + 1);
    for (int i = 0; i < len; i++) {
        buffer[i] = toupper(v.string_val[i]);
    }
    buffer[len] = '\0';
    Value result = create_string(buffer);
    free(buffer);
    return result;
}

// lower() for strings
Value lower_val(Value v) {
    if (v.type != TYPE_STRING) {
        fprintf(stderr, "TypeError: lower() expects a string\n");
        exit(1);
    }
    int len = strlen(v.string_val);
    char* buffer = (char*)malloc(len + 1);
    for (int i = 0; i < len; i++) {
        buffer[i] = tolower(v.string_val[i]);
    }
    buffer[len] = '\0';
    Value result = create_string(buffer);
    free(buffer);
    return result;
}

// isinstance() simplified: check type equality
Value isinstance_val(Value v, ValueType type) {
    return create_int(v.type == type);
}

// sorted() simplified: only for list of ints, returns new sorted list
int cmp_int(const void* a, const void* b) {
    Value* va = (Value*)a;
    Value* vb = (Value*)b;
    if (va->type != TYPE_INT || vb->type != TYPE_INT) {
        fprintf(stderr, "TypeError: sorted() supports only list of ints\n");
        exit(1);
    }
    return va->int_val - vb->int_val;
}

Value sorted_val(Value list) {
    if (list.type != TYPE_LIST) {
        fprintf(stderr, "TypeError: sorted() expects a list\n");
        exit(1);
    }
    Value copy = create_list(list.list_val.count);
    for (int i = 0; i < list.list_val.count; i++) {
        copy.list_val.items[i] = list.list_val.items[i];
    }
    qsort(copy.list_val.items, copy.list_val.count, sizeof(Value), cmp_int);
    return copy;
}

Value set_val(Value v) {
    if (v.type != TYPE_LIST) {
        fprintf(stderr, "TypeError: set() expects a list\n");
        exit(1);
    }
    Value set = create_set(v.list_val.count);
    int count = 0;
    for (int i = 0; i < v.list_val.count; i++) {
        int found = 0;
        for (int j = 0; j < count; j++) {
            if (set.set_val.items[j].int_val == v.list_val.items[i].int_val) {
                found = 1;
                break;
            }
        }
        if (!found) {
            set.set_val.items[count++] = v.list_val.items[i];
        }
    }
    set.set_val.count = count;
    return set;
}

Value make_dict(int lenght, Value* keys, Value* values) {
    Value dict = create_dict(lenght);
    for (int i = 0; i < lenght; i++) {
        dict.dict_val.keys[i] = keys[i];
        dict.dict_val.values[i] = values[i];
    }
    return dict;
}

Value make_list(int lenght, Value* items) {
    Value list = create_list(lenght);
    for (int i = 0; i < lenght; i++) {
        list.list_val.items[i] = items[i];
    }
    return list;
}

Value make_tuple(int lenght, Value* items) {
    Value tuple = create_tuple(lenght);
    for (int i = 0; i < lenght; i++) {
        tuple.tuple_val.items[i] = items[i];
    }
    return tuple;
}

bool is_none(Value v) {
    return v.type == TYPE_NONE;
}


#endif // RUNTIME_C
