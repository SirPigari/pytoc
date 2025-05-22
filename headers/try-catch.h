#ifndef TRYCATCH_H
#define TRYCATCH_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#include <sys/wait.h>
#endif

#define STDERR_BUF_SIZE 1024

typedef struct {
    int triggered;
    char stderr_buf[STDERR_BUF_SIZE];
    int status_code;
} TryCatchContext;

#ifdef _WIN32

#define TRY(ctx_ptr) \
    do { \
        SECURITY_ATTRIBUTES saAttr = { sizeof(SECURITY_ATTRIBUTES), NULL, TRUE }; \
        HANDLE readPipe, writePipe; \
        CreatePipe(&readPipe, &writePipe, &saAttr, 0); \
        SetHandleInformation(readPipe, HANDLE_FLAG_INHERIT, 0); \
        PROCESS_INFORMATION pi; \
        STARTUPINFOA si; \
        ZeroMemory(&si, sizeof(si)); \
        si.cb = sizeof(si); \
        si.hStdError = writePipe; \
        si.dwFlags |= STARTF_USESTDHANDLES; \
        ZeroMemory(&pi, sizeof(pi)); \
        char cmdLine[256]; \
        snprintf(cmdLine, sizeof(cmdLine), "\"%s\"", GetCommandLineA()); /* You’ll want to replace this */ \
        if (CreateProcessA(NULL, cmdLine, NULL, NULL, TRUE, 0, NULL, NULL, &si, &pi)) { \
            CloseHandle(writePipe); \
            DWORD bytesRead = 0; \
            ReadFile(readPipe, (ctx_ptr)->stderr_buf, sizeof((ctx_ptr)->stderr_buf) - 1, &bytesRead, NULL); \
            (ctx_ptr)->stderr_buf[bytesRead] = '\0'; \
            WaitForSingleObject(pi.hProcess, INFINITE); \
            DWORD exitCode = 0; \
            GetExitCodeProcess(pi.hProcess, &exitCode); \
            (ctx_ptr)->status_code = (int)exitCode; \
            (ctx_ptr)->triggered = (exitCode != 0 || (ctx_ptr)->stderr_buf[0] != '\0'); \
            CloseHandle(pi.hProcess); \
            CloseHandle(pi.hThread); \
            CloseHandle(readPipe); \
            TryCatchContext* exc_ptr = (ctx_ptr); \
            if ((ctx_ptr)->triggered) {

#define CATCH(ctx_ptr, exc_ptr) \
            }

#define END_TRY(ctx_ptr) \
        } else { \
            fprintf(stderr, "Failed to create process\n"); \
            exit(1); \
        } \
    } while (0)

#else // POSIX version

#define TRY(ctx_ptr) \
    do { \
        int pipefd[2]; \
        pipe(pipefd); \
        pid_t pid = fork(); \
        if (pid == 0) { \
            dup2(pipefd[1], STDERR_FILENO); \
            close(pipefd[0]); \
            close(pipefd[1]);

#define CATCH(ctx_ptr, exc_ptr) \
	    exit(0); \
	} else if (pid > 0) { \
	    close(pipefd[1]); \
	    read(pipefd[0], (ctx_ptr)->stderr_buf, sizeof((ctx_ptr)->stderr_buf) - 1); \
	    close(pipefd[0]); \
	    int wstatus; \
	    waitpid(pid, &wstatus, 0); \
	    (ctx_ptr)->triggered = (wstatus != 0 || (ctx_ptr)->stderr_buf[0] != '\0'); \
	    (ctx_ptr)->status_code = WEXITSTATUS(wstatus); \
	    exc_ptr = (ctx_ptr); \
	    if ((ctx_ptr)->triggered) {



#define END_TRY(ctx_ptr) \
            } \
        } else { \
            perror("fork failed"); \
            exit(1); \
        } \
    } while (0)

#endif // _WIN32

#endif // TRYCATCH_H
