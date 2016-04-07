# import-profiler
A basic python import profiler to find bottlenecks in import times

This is Work in Progress. To try it out, write something as follows:

``` python
import import_profiler
import_profiler.enable()

# Anything expensive in here
import requests

# Print cumulative and inline times. The number of + in the 3rd column
# indicates the depth of the stack.
import_profiler.print_info(import_debug._IMPORT_STACK)
```
