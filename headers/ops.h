#ifndef OPS_H
#define OPS_H

#include "runtime.h"
#include "_global.h"

#include <stdarg.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>


Value add_values(Value a, Value b);

Value sub_values(Value a, Value b);

Value mul_values(Value a, Value b);

Value div_values(Value a, Value b);

Value join_strings(int count, ...);

#endif // OPS_H
