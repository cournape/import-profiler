# import-profiler
A basic python import profiler to find bottlenecks in import times. While not
often a problem, imports can be an issue for applications that need to start
quickly, such as CLI tools. The goal of import profiler is to help find the
bottlenecks when importing a given package.

## Example

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

# Missing features

We don't track where imports happen: it would be nice to know where a given
import in the profile output happens.
