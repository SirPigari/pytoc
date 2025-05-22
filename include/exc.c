#ifndef EXC_C
#define EXC_C

#include "../headers/exc.h"
#include "runtime.c"
#include "_global.c"
#include "try-catch.c"

void init_exc() {
    ValueError = create_string("ValueError");
    TypeError = create_string("TypeError");
    ZeroDivisionError = create_string("ZeroDivisionError");
}

// These macros ensure we don't overflow the buffer
#define SAFE_SNPRINTF(buf, fmt, ...) \
    snprintf((buf), sizeof((ctx)->stderr_buf), (fmt), __VA_ARGS__)

// For subprocess-based try-catch: exit after writing to stderr_buf
void raise_exception(TryCatchContext* ctx, const char* name, const char* message) {
    ctx->triggered = 1;
    SAFE_SNPRINTF(ctx->stderr_buf, "%s: %s", name, message);
    fflush(stderr); // in case stderr is redirected
    exit(1);        // Terminate child or subprocess cleanly
}

void raise_exception_with_value(TryCatchContext* ctx, const char* name, const char* message, Value value) {
    ctx->triggered = 1;
    SAFE_SNPRINTF(ctx->stderr_buf, "%s: %s (value: %s)", name, message, to_string(value));
    fflush(stderr);
    exit(1);
}

void raise_exception_with_context(TryCatchContext* ctx, const char* name, const char* message, TryCatchContext* context) {
    ctx->triggered = 1;
    SAFE_SNPRINTF(ctx->stderr_buf, "%s: %s", name, message);
    fflush(stderr);
    exit(1);
}

void raise_exception_full(TryCatchContext* ctx, const char* name, const char* message, Value value, TryCatchContext* context, const char* extra) {
    ctx->triggered = 1;
    SAFE_SNPRINTF(ctx->stderr_buf, "%s: %s | Extra: %s | Value: %s", name, message, extra, to_string(value));
    fflush(stderr);
    exit(1);
}

void print_exception(TryCatchContext* ctx) {
    if (ctx->triggered && ctx->stderr_buf[0] != '\0') {
        fprintf(stderr, "%s\n", ctx->stderr_buf);
    }
}

void clear_exception(TryCatchContext* ctx) {
    memset(ctx->stderr_buf, 0, sizeof(ctx->stderr_buf));
    ctx->triggered = 0;
}

Value make_value_from_exc(TryCatchContext* ctx) {
    if (ctx->triggered && ctx->stderr_buf[0] != '\0') {
        return create_string(ctx->stderr_buf);
    }
    return create_none();
}

#endif // EXC_C
