#ifndef EXC_H
#define EXC_H

#include "runtime.h"
#include "ops.h"
#include "_global.h"
#include "try-catch.h"

Value ValueError;
Value TypeError;
Value ZeroDivisionError;


void raise_exception(TryCatchContext* ctx, const char* name, const char* message);
void clear_exception(TryCatchContext* ctx);
void print_exception(TryCatchContext* ctx);
Value make_value_from_exc(TryCatchContext* ctx);

// Optional extended raise helpers
void raise_exception_with_value(TryCatchContext* ctx, const char* name, const char* message, Value value);
void raise_exception_with_context(TryCatchContext* ctx, const char* name, const char* message, TryCatchContext* other);
void raise_exception_full(TryCatchContext* ctx, const char* name, const char* message, Value value, TryCatchContext* other, const char* extra);

#endif // EXC_H
