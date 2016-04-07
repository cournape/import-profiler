# import-profiler
A basic python import profiler to find bottlenecks in import times. While not
often a problem, imports can be an issue for applications that need to start
quickly, such as CLI tools. The goal of import profiler is to help find the
bottlenecks when importing a given package.

## Example

This is Work in Progress. To try it out, write something as follows:

``` python
from import_profiler import profile_import

with profile_import() as context:
    # Anything expensive in here
    import requests

# Print cumulative and inline times. The number of + in the 3rd column
# indicates the depth of the stack.
context.print_info()
```

Output:

```
  cumtime (ms)    intime (ms)  name
          83              0.5  requests
          55              0.5  +packages.urllib3.contrib
          54.1            0.3  ++
          53.1            0.7  +++connectionpool
           6.3            1.1  ++++logging
           1.4            0.5  +++++collections
           2.7            1.3  +++++threading
           1.4            0.3  ++++++re
           7              0.7  ++++socket
           5.7            5.7  +++++_ssl
           7              0.1  ++++packages.ssl_match_hostname
           6.9            0.1  +++++
           6.8            2.3  ++++++ssl
           3.2            1.5  +++++++textwrap
           1.7            1.6  ++++++++string
          12              0.4  ++++connection
           7.7            1.1  +++++httplib
           2.3            2.3  ++++++urlparse
           4.2            0.2  ++++++mimetools
           3.4            0.3  +++++++tempfile
           2.1            1.4  ++++++++random
           3.6            0.1  +++++util.ssl_
           1.1            1    ++++++url
          16.4            0.2  ++++request
           1.5            1.4  +++++urllib.parse
          14.7            0.2  +++++filepost
           9.1            6    ++++++uuid
           2.9            1.7  +++++++ctypes
           5.4            0.2  ++++++fields
           4.8            1.7  +++++++email.utils
           2.4            0.2  ++++++++email._parseaddr
           2.2            0.7  +++++++++calendar
           1.4            1.4  ++++++++++locale
           1.2            0.4  ++++response
          24.8            0.4  +
           1.8            1.7  ++cgi
           5.4            5.4  ++platform
          15.1            0.1  ++compat
           2.4            0.2  +++json
           1.5            0.5  ++++decoder
           1.6            1.3  +++urllib2
           7.6            6.8  +++cookielib
           3              2.5  +++Cookie
           1.5            0.6  +models
           1              0.1  +api
```

# Missing features

We don't track where imports happen: it would be nice to know where a given
import in the profile output happens.
