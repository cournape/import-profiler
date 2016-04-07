import collections
import time


__OLD_IMPORT = None


class ImportInfo(object):
    def __init__(self, name, context_name, counter):
        self.name = name
        self.context_name = context_name
        self._counter = counter
        self._depth = 0
        self._start = time.time()

        self.elapsed = None

    def done(self):
        self.elapsed = time.time() - self._start

    @property
    def _key(self):
        return self.name, self.context_name, self._counter

    def __repr__(self):
        return "ImportInfo({!r}, {!r}, {!r})".format(*self._key)

    def __hash__(self):
        return hash(self._key)

    def __eq__(self, other):
        if isinstance(other, ImportInfo):
            return other._key == self._key
        return NotImplemented

    def __ne__(self):
        return not self == other


class ImportStack(object):
    def __init__(self):
        self._current_stack = []
        self._full_stack = collections.defaultdict(list)
        self._counter = 0

    def push(self, name, context_name):
        info = ImportInfo(name, context_name, self._counter)
        self._counter += 1

        if len(self._current_stack) > 0:
            parent = self._current_stack[-1]
            self._full_stack[parent].append(info)
        self._current_stack.append(info)

        info._depth = len(self._current_stack) - 1

        return info

    def pop(self, import_info):
        top = self._current_stack.pop()
        assert top is import_info
        top.done()


def compute_intime(parent, full_stack, ordered_visited, visited, depth=0):
    if parent in visited:
        return

    cumtime = intime = parent.elapsed
    visited[parent] = [cumtime, parent.name, parent.context_name, depth]
    ordered_visited.append(parent)

    for child in full_stack[parent]:
        intime -= child.elapsed
        compute_intime(child, full_stack, ordered_visited, visited, depth + 1)

    visited[parent].append(intime)


def print_info(import_stack):
    full_stack = import_stack._full_stack

    keys = sorted(full_stack.keys(), key=lambda p: p._counter)
    visited = {}
    ordered_visited = []

    for key in keys:
        compute_intime(key, full_stack, ordered_visited, visited)

    lines = []
    for k in ordered_visited:
        node = visited[k]
        cumtime = node[0] * 1000
        name = node[1]
        context_name = node[2]
        level = node[3]
        intime = node[-1] * 1000
        if cumtime > 1:
            lines.append((
                "{:.1f}".format(cumtime),
                "{:.1f}".format(intime),
                "+" * level + name,
            ))

    import tabulate

    print(
        tabulate.tabulate(
            lines, headers=("cumtime (ms)", "intime (ms)", "name"), tablefmt="plain")
    )

_IMPORT_STACK = ImportStack()


def profiled_import(name, globals=None, locals=None, fromlist=None,
                    level=-1, *a, **kw):
    if globals is None:
        context_name = None
    else:
        context_name = globals.get("__name__")
        if context_name is None:
            context_name = globals.get("__file__")

    info = _IMPORT_STACK.push(name, context_name)
    try:
        return __OLD_IMPORT(name, globals, locals, fromlist, level, *a, **kw)
    finally:
        _IMPORT_STACK.pop(info)


def enable():
    global __OLD_IMPORT
    __OLD_IMPORT = __builtins__["__import__"]
    __builtins__["__import__"] = profiled_import


def disable():
    __builtins__["__import__"] = __OLD_IMPORT
