# Inteligencia semántica de código

[English](../semantic-code-intelligence.md)

AAK separa el descubrimiento interactivo del compilador de la evidencia
arquitectónica determinista. AAK conserva la autoridad y la conformidad; un
proveedor semántico como Roslynk descubre relaciones resueltas por el
compilador; Git, el build y los tests prueban el estado y el comportamiento.

## Flujo del agente

En .NET, descubre una solución existente y, si Roslynk está configurado, ábrela
una vez y espera a que esté lista. Prefiere sus operaciones read-only de
símbolos, definiciones, referencias, callers, implementaciones, jerarquías y
diagnósticos sobre la búsqueda textual. Registra proveedor, cobertura y si cada
conclusión es semántica, sintáctica, textual, inferida o desconocida. Los
diagnósticos aceleran la edición, pero no sustituyen el build ni los tests.

Si Roslynk falta o está incompleto, usa el adapter y el fallback de `aak
context`, declara la menor resolución y conserva visibles `Indexing`,
`Ambiguous`, `NotFound`, `Stale`, `Conflict`, la cobertura parcial y la
truncación.

## Contrato de validación

La validación semántica se activa explícitamente en project policy con las keys
`observation.semantic.provider`, `mode`, `solution` y `capabilities`. El nombre
selecciona exactamente un entry point
`agentic_architecture_kit.semantic_observers` cuya distribución está pinneada
en `.agentic/toolchain.json`.

```json
{
  "observation": {
    "semantic": {
      "provider": "roslynk",
      "mode": "advisory",
      "solution": "Product.slnx",
      "capabilities": ["source-dependencies"]
    }
  }
}
```

`advisory` usa evidencia cuando existe y declara el fallback. `required` deja
como review-required la ausencia, cobertura parcial o truncación y falla ante
evidencia obsoleta, malformada, incompatible o que escape del repositorio. La
observación declara proveedor/versión, revisión, sujeto, cobertura,
configuraciones, exclusiones, diagnósticos estructurados, edges semánticos y un
manifest de inputs relativos con hashes SHA-256.

La cobertura completa sólo sustituye candidates de menor resolución en
archivos cubiertos. La parcial o ausente conserva el fallback sintáctico. Un
edge observado nunca modifica policy ni concede permiso. `aak context status`
muestra proveedor, cobertura, resolución, fingerprint, fallback y degradación.

La degradación machine-readable usa códigos estables:
`PROVIDER_NOT_CONFIGURED`, `PROVIDER_NOT_INSTALLED`, `PROVIDER_NOT_PINNED`,
`PROVIDER_AMBIGUOUS`, `PROVIDER_UNAVAILABLE`, `SUBJECT_NOT_FOUND`,
`SUBJECT_AMBIGUOUS`, `INDEXING_INCOMPLETE`, `UNSUPPORTED_CONFIGURATION`,
`PARTIAL_COVERAGE`, `TRUNCATED_RESULT`, `STALE_INPUT`, `INPUT_HASH_MISMATCH`,
`PATH_ESCAPE`, `INVALID_PROVIDER_OUTPUT` y `CAPABILITY_NOT_PROVIDED`. Los
providers deben usar diagnósticos estructurados y no convertir errores
operacionales en un conjunto vacío de dependencias.

## Límite con Roslynk

Roslynk no es dependencia del package principal. El bridge real pertenece a una
distribución `aak-dotnet-roslynk` separada y exige una exportación masiva,
estable, machine-readable y sin truncación oculta. Los outlines interactivos o
una llamada `find_references` por símbolo no son evidencia exhaustiva de CI.
