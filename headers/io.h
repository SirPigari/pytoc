#ifndef IO_H
#define IO_H

#include "_global.h"

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

ssize_t getline(char **lineptr, size_t *n, FILE *stream);

Value print(Value v, Value sep_val, Value end_val);
Value input(Value prompt_val);

#endif // IO_H