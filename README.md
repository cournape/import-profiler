# import-profiler
A basic python import profiler to find bottlenecks in import times

This is Work in Progress. To try it out, write something as follows:

``` python
from import_profiler import profile_import

with profile_import as context:
    # Anything expensive in here
    import requests

# Print cumulative and inline times. The number of + in the 3rd column
# indicates the depth of the stack.
context.print_info()
```
