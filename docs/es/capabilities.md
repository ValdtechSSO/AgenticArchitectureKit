# Estado de implementación

Agentic Architecture Kit está actualmente en **preview 0.4**. El núcleo de
decisiones y las referencias portables incluidas son el objetivo normativo; esta
página declara qué puede demostrar hoy la implementación. La documentación por
sí sola no se presenta como implementada.

| Capacidad | Estado | Garantía actual |
|---|---|---|
| Reglas portables / policy de proyecto / waivers | Implementado | Entradas separadas y validadas por schema; un waiver produce `WAIVED`, nunca `PASS` |
| Distribución versionada | Implementado | Un package Python agrupa CLI, reglas, schemas, plantillas y adaptadores; se comprueban los pins del consumidor y existe export offline explícito con manifiesto de digests |
| Autovalidación | Implementado | Smoke test estructural y autorización de imports reales host CLI → validator; los casos prohibidos y entre módulos se ejercitan en tests/ejemplos, no inventándolos en el kit |
| Observación .NET | Implementado | Proyectos SDK, `ProjectReference`, namespaces C# y directivas `using` |
| Observación Python | Implementado | `pyproject.toml`, paquetes/CLI directos e imports obtenidos del AST |
| Dependencias dentro de un assembly | Inicial | Correspondencia exacta de namespace/import en C# y Python; no es un modelo semántico completo del compilador |
| Protección del crecimiento de policy | Implementado | `--base-ref` detecta nuevos límites y permisos; CI compara PR con su base y push con su SHA anterior |
| Integridad de entradas y resultados | Implementado | Los resultados contienen digests canónicos de toolchain, policy, waivers, reviews, autoridades, catálogo y observaciones |
| Integridad de referencias normativas | Implementado | Cada hallazgo contiene referencia incluida y digest semántico por regla; `DOC001` valida headings, clasificación, referencias de módulo y cobertura completa del documento del validador |
| Diagnóstico contextual de reglas | Implementado | `aak core` expone el contexto preventivo y `aak explain RULE` combina definición, digest, hallazgos, scope, evidencia y concesiones aplicadas |
| Revisiones semánticas persistentes | Implementado | La integridad local exige huella exacta, SHA ancestro alcanzable, autoridad declarada, principal CODEOWNER y evidencia; la aprobación real se aplica externamente |
| Invalidación semántica de concesiones | Implementado | El schema rechaza un digest ausente; un digest válido pero obsoleto no se aplica y exige revisión; cambios de otras reglas no lo invalidan |
| Aplicación de autoridad | Garantía dividida | Cada scope protegido exige cobertura CODEOWNERS real y los overrides no pueden retirar sus principals; la protección de rama y la aprobación real siguen siendo hechos de plataforma |
| Higiene de waivers | Implementado | Waivers sin uso, inválidos, caducados o demasiado amplios permanecen visibles |
| Índice generado del repositorio | Inicial | Índices JSON de módulos, proyectos, dependencias, documentos y tests ligados a revisión |
| Comandos de contexto progresivo | Inicial | Locate, búsqueda textual exacta de símbolos/referencias/tests e impacto directo con procedencia |
| Evidencia por tarea | Inicial | Se pueden retener resultado de arquitectura y manifiesto de digest por tarea y revisión |
| Pureza de comportamiento del host | Hoja de ruta | `HOST001` solo demuestra ubicación; la propiedad del comportamiento requiere un analizador semántico |
| Ownership observado de escrituras | Hoja de ruta | Se valida la unicidad declarada; las escrituras reales siguen siendo revisables |
| Grafo de símbolos de nivel compilador | Hoja de ruta | La búsqueda actual es texto exacto y declara explícitamente esa confianza |
| Ledger completo de build/test/evidencia | Hoja de ruta | El kit retiene evidencia arquitectónica; todavía no orquesta todas las herramientas del proyecto |

“Inicial” significa utilizable con una garantía deliberadamente limitada. No
significa que se haya completado la capacidad semántica más amplia del manifiesto.

## Criterio de entrega

Una capacidad pasa a **Implementado** solo cuando tiene comando o contrato
público, tests automáticos y ejemplo funcional cuando corresponde. Se usa
dogfooding cuando el kit dispone de un sujeto real legítimo; los casos prohibidos
se demuestran con fixtures ejecutables en lugar de crear límites artificiales en
producción. El comportamiento solo documentado permanece en **Hoja de ruta**.

## Capas de evidencia

- **Autovalidación:** demuestra que el adaptador Python funciona sobre el kit,
  que estructura declarada y observada coinciden y que los imports reales host →
  módulo están autorizados. No inventa un segundo módulo para ejercitar una regla.
- **Tests de conformidad:** demuestran la mecánica de reglas, reviews obsoletas,
  revisiones inalcanzables, autoridad inválida, crecimiento de policy, waivers
  amplios y dependencias permitidas o prohibidas.
- **Ejemplos:** demuestran el consumo sin vendorización: un repositorio .NET pasa y
  otro, compilable y de un solo assembly, falla por dependencia módulo → host.
- **Controles de plataforma:** demuestran quién aprobó y si se impidió la
  mutación directa. El repositorio los declara, pero no puede observar por sí
  solo la protección de rama de GitHub.
