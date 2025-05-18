#ifndef RUNTIME_H
#define RUNTIME_H

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdbool.h>
#include "_global.h"

const char* type_name(ValueType t);


Value to_int(Value v);
Value to_string(Value v);
Value len(Value v);
Value abs_val(Value v);
Value max_val(Value list);
Value min_val(Value list);
Value sum_val(Value list);
Value bool_val(Value v);
Value ord_val(Value v);
Value chr_val(Value v);
Value range_val(Value start, Value stop, Value step);
Value range_stop(Value stop);
Value range_start_stop(Value start, Value stop);
Value reversed_val(Value v);
Value upper_val(Value v);
Value lower_val(Value v);
Value isinstance_val(Value v, ValueType type);
int cmp_int(const void* a, const void* b);
Value sorted_val(Value list);
Value set_val(Value v);
Value make_dict(int lenght, Value* keys, Value* values);
Value make_list(int lenght, Value* items);
Value make_tuple(int lenght, Value* items);
bool is_none(Value v);

#endif // RUNTIME_H
