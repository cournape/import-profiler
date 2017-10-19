import operator
import time

from attr import attr, attributes, Factory


@attributes(frozen=True)
class ImportInfo(object):
    name = attr()
    context_name = attr()

    counter = attr()
    start = attr(default=Factory(time.time))


class ImportStack(object):
    def __init__(self):
        self._current_stack = []
        self._full_stack = {}
        self._elapsed = {}  # ImportInfo instances -> elapsed times
        self._counter = 0

    def push(self, name, context_name):
        info = ImportInfo(name, context_name, self._counter)
        self._counter += 1

        if len(self._current_stack) > 0:
            parent = self._current_stack[-1]
            if parent not in self._full_stack:
                self._full_stack[parent] = []
            self._full_stack[parent].append(info)
        self._current_stack.append(info)

        return info

    def pop(self, import_info):
        top = self._current_stack.pop()
        assert top is import_info
        self._elapsed[top] = time.time() - top.start


def compute_intime(parent, full_stack, elapsed, ordered_visited, visited, depth=0):
    if parent in visited:
        return

    cumtime = intime = elapsed[parent]
    visited[parent] = [cumtime, parent.name, parent.context_name, depth]
    ordered_visited.append(parent)

    for child in full_stack.get(parent, []):
        intime -= elapsed[child]
        compute_intime(child, full_stack, elapsed, ordered_visited, visited, depth + 1)

    visited[parent].append(intime)


class ImportProfilerContext(object):
    def __init__(self):
        self._original_importer = __builtins__["__import__"]
        self._import_stack = ImportStack()

    def enable(self):
        __builtins__["__import__"] = self._profiled_import

    def disable(self):
        __builtins__["__import__"] = self._original_importer

    def print_info(self, threshold=1.):
        """ Print profiler results.

        Parameters
        ----------
        threshold : float
            import statements taking less than threshold (in ms) will not be
            displayed.
        """
        full_stack = self._import_stack._full_stack
        elapsed = self._import_stack._elapsed

        keys = sorted(full_stack.keys(), key=operator.attrgetter("counter"))
        visited = {}
        ordered_visited = []

        for key in keys:
            compute_intime(key, full_stack, elapsed, ordered_visited, visited)

        lines = []
        for k in ordered_visited:
            node = visited[k]
            cumtime = node[0] * 1000
            name = node[1]
            context_name = node[2]
            level = node[3]
            intime = node[-1] * 1000
            if cumtime >= threshold:
                lines.append((
                    "{:.1f}".format(cumtime),
                    "{:.1f}".format(intime),
                    "+" * level + name,
                ))

        # Import here to avoid messing with the profile
        import tabulate

        print(
            tabulate.tabulate(
                lines, headers=("cumtime (ms)", "intime (ms)", "name"), tablefmt="plain")
        )

    # Protocol implementations
    def __enter__(self):
        self.enable()
        return self

    def __exit__(self, *a, **kw):
        self.disable()

    def _profiled_import(self, name, globals=None, locals=None, fromlist=None,
                         level=-1, *a, **kw):
        if globals is None:
            context_name = None
        else:
            context_name = globals.get("__name__")
            if context_name is None:
                context_name = globals.get("__file__")

        info = self._import_stack.push(name, context_name)
        try:
            return self._original_importer(name, globals, locals, fromlist, level, *a, **kw)
        finally:
            self._import_stack.pop(info)


def profile_import():
    return ImportProfilerContext()
