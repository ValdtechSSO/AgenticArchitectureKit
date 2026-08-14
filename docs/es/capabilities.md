# Estado de implementación

Agentic Architecture Kit está actualmente en **preview 0.2**. El manifiesto es
el objetivo normativo; esta página declara qué puede demostrar hoy la
implementación de referencia. Un requisito del manifiesto no se presenta como
implementado solo porque esté documentado.

| Capacidad | Estado | Garantía actual |
|---|---|---|
| Reglas portables / policy de proyecto / waivers | Implementado | Entradas separadas y validadas por schema; un waiver produce `WAIVED`, nunca `PASS` |
| Autovalidación | Implementado | El kit tiene policy Python y valida su propio límite compacto módulo/host |
| Observación .NET | Implementado | Proyectos SDK, `ProjectReference`, namespaces C# y directivas `using` |
| Observación Python | Implementado | `pyproject.toml`, paquetes/CLI directos e imports obtenidos del AST |
| Dependencias dentro de un assembly | Inicial | Correspondencia exacta de namespace/import en C# y Python; no es un modelo semántico completo del compilador |
| Protección del crecimiento de policy | Implementado | `--base-ref` detecta nuevos límites y permisos de dependencia y exige referencias a decisiones |
| Integridad de entradas y resultados | Implementado | Los resultados contienen digests canónicos de policy, waivers, reviews, catálogo y observaciones |
| Revisiones semánticas persistentes | Implementado | Un acuse solo vale para la huella exacta del hallazgo y queda obsoleto cuando cambia el sujeto |
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
público, tests automáticos, ejemplo funcional cuando corresponde, y el kit puede
ejercitarla contra sí mismo. El comportamiento solo documentado permanece en
**Hoja de ruta**.
