import re
def fake_decompile(func, seekdef = False):
    with open(func.__globals__['__file__']) as f:
        lines = f.readlines()
    positions = list(func.__code__.co_positions())
    start = min([i[0] for i in positions if i[0] is not None])
    end = max([i[1] for i in positions if i[1] is not None])

    if seekdef:
        pattern = re.compile(f"\\s*def\\s+{func.__name__}\\s*\\(")
        while True:
            if pattern.match(lines[start]):
                break
            start -= 1
            if start < 0:
                raise RuntimeError("Could not find start of function definition.  Is it a lambda?")
        print(18, start, end)
        return str.join("", lines[start:end])
    else: # Do our best to reconstruct a suitable signature, this should work passably even for lambdas
        names = func.__code__.co_varnames
        argcount = func.__code__.co_argcount
        kwonly = func.__code__.co_kwonlyargcount
        posonly = func.__code__.co_posonlyargcount
        defaults = func.__defaults__
        kwdefaults = func.__kwdefaults__
        varargs = func.__code__.co_flags & 4
        kwvarargs = func.__code__.co_flags & 8
        args = []
        kw = []
        for i in range(argcount):
            args.append(names[i])
        for i in range(kwonly):
            kw.append(names[i+argcount])
        if defaults:
            for i in reversed(defaults):
                args[-1 -i] += f"={repr(i)}"
        for idx, i in enumerate(kw):
            if i in kwdefaults:
               kw[idx] += f"={repr(kwdefaults[i])}"
        if varargs:
            va = names[argcount+kwonly]
            args.append(f"*{va}")
        if kwvarargs:
            kwa = names[argcount+kwonly+bool(varargs)]
            kw.append(f"**{kwa}")
        if posonly:
            args.insert(posonly, "/")
        if kwonly and not varargs:
            args.append("*")

        args.extend(kw)
        signature = f"def {func.__name__}({str.join(', ', args)}):\n"
        return str.join("", [signature, *lines[start:end]])
