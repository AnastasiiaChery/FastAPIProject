---
paths: "**/*.{pyx,pxd}"
---

# Cython Guidelines

## General
- Use `.pyx` for implementation files, `.pxd` for declarations/headers
- Always add type annotations — untyped Cython is just slow Python
- Prefer `cdef` for internal functions, `cpdef` for functions called from both Python and C

## Types
- Use C types (`int`, `double`, `long`) for numeric variables in hot paths
- Use `cdef` typed memoryviews for array access: `double[:] arr`
- Avoid Python objects in inner loops — box/unbox outside the loop

## Performance
- Add `# cython: boundscheck=False, wraparound=False` at the top of performance-critical files
- Use `with nogil:` blocks for CPU-bound work that doesn't touch Python objects
- Profile before optimising — measure actual bottlenecks

## Build
- Build with `python setup.py build_ext --inplace` or via `uv run`
- Check generated C code with `cython -a file.pyx` to spot Python overhead (yellow lines)
