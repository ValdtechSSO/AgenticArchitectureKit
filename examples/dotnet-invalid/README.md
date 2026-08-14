# Intentionally invalid .NET example

This example places the Orders module and CLI host in one .NET assembly and adds
a source-level import from Orders to the host namespace. `DEP001` fails without
any `ProjectReference`, demonstrating that dependency rules also have teeth in
the compact structure preferred by the manifesto.

```sh
python3 tools/architecture/validate.py \
  --root examples/dotnet-invalid
```

The expected exit code is `1` and the result contains `FAIL DEP001`.
