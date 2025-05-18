#ifndef IO_C
#define IO_C

#include "../headers/io.h"
#include "_global.c"

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

ssize_t _getline(char **lineptr, size_t *n, FILE *stream) {
    if (!lineptr || !n || !stream) return -1;

    size_t pos = 0;

    if (*lineptr == NULL || *n == 0) {
        *n = 128;
        *lineptr = malloc(*n);
        if (!*lineptr) return -1;
    }

    int c = fgetc(stream);
    if (c == EOF) return -1;

    do {
        if (pos + 1 >= *n) {
            size_t new_size = *n * 2;
            char *new_ptr = realloc(*lineptr, new_size);
            if (!new_ptr) return -1;
            *lineptr = new_ptr;
            *n = new_size;
        }

        (*lineptr)[pos++] = c;
        if (c == '\n') break;
    } while ((c = fgetc(stream)) != EOF);

    (*lineptr)[pos] = '\0';
    return pos;
}

Value print(Value v, Value sep_val, Value end_val) {
    const char* sep = " ";
    const char* end = "\n";

    if (sep_val.type == TYPE_STRING && sep_val.string_val != NULL) {
        sep = sep_val.string_val;
    }

    if (end_val.type == TYPE_STRING && end_val.string_val != NULL) {
        end = end_val.string_val;
    }

    // Assume v is always a LIST
    for (int i = 0; i < v.list_val.count; ++i) {
        print_value(v.list_val.items[i]);
        if (i < v.list_val.count - 1) {
            printf("%s", sep);
        }
    }

    printf("%s", end);
    fflush(stdout);
    return None;
}

Value input(Value prompt_val) {
    if (prompt_val.type == TYPE_STRING && prompt_val.string_val != NULL) {
        print_value(prompt_val);
        fflush(stdout);
    }

    char* buffer = NULL;
    size_t size = 0;

    ssize_t len = _getline(&buffer, &size, stdin);

    if (len == -1 || buffer == NULL) {
        if (buffer) free(buffer);
        return create_string("");
    }

    if (len > 0 && buffer[len - 1] == '\n') {
        buffer[len - 1] = '\0';
    }

    Value result = create_string(buffer);
    free(buffer);
    return result;
}


#endif // IO_C
