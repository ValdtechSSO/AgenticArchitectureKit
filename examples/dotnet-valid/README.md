# Valid .NET example

This compact repository has one functional module and one CLI host. Its host may
reference the module; the module cannot reference the host.

From the kit root:

```sh
python3 tools/architecture/validate.py \
  --root examples/dotnet-valid
```

The run has no `FAIL` result. Semantic findings remain visible until a project
authority records a fingerprint-bound review.
