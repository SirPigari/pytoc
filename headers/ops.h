#ifndef OPS_H
#define OPS_H

#define FLOAT_EPSILON 1e-9

#include "runtime.h"
#include "_global.h"

#include <stdarg.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>  // For pow, floor, fmod

Value add_values(Value a, Value b);

Value sub_values(Value a, Value b);

Value mul_values(Value a, Value b);

Value div_values(Value a, Value b);

Value pow_values(Value a, Value b);

Value floordiv_values(Value a, Value b);

Value mod_values(Value a, Value b);

Value join_strings(int count, ...);

// Comparisons

Value eq_values(Value a, Value b);

Value ne_values(Value a, Value b);

Value lt_values(Value a, Value b);

Value le_values(Value a, Value b);

Value gt_values(Value a, Value b);

Value ge_values(Value a, Value b);

// Unary operations
Value neg_values(Value a);

Value pos_values(Value a);

Value not_values(Value a);

// Assert
Value assert(Value condition, Value message);

#endif // OPS_H
