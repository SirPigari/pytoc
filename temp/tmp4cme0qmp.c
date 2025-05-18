#include "C:\Users\sirpigari\Desktop\Projects\PythonToC\include\_global.c"
#include "C:\Users\sirpigari\Desktop\Projects\PythonToC\include\runtime.c"
#include "C:\Users\sirpigari\Desktop\Projects\PythonToC\include\ops.c"
#include "C:\Users\sirpigari\Desktop\Projects\PythonToC\include\io.c"

Value add(Value a, Value b) {
    return add_values(a, b);
}
Value _maincfcd2084() {
    Value _print_argscfcd2084[1] = { create_string("Welcome to PYTOC demo!") };
    print(make_list(1, _print_argscfcd2084), create_string(" "), create_string("\n"));
    Value x = to_int(input(create_string("Enter first number: ")));
    Value y = to_int(input(create_string("Enter second number: ")));
    Value result = add(x, y);
    Value _print_argsc4ca4238[2] = { create_string("The sum is:"), result };
    print(make_list(2, _print_argsc4ca4238), create_string(" "), create_string("\n"));
}

int main() {
    _maincfcd2084();
    return 0;
}