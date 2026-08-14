# Agentic Architecture Kit

[English — canonical](../../README.md) · [Política lingüística](language-policy.md)

> **Estado de implementación:** preview 0.4.3. La distribución publicada es
> autosuficiente para el bootstrap y la evolución por agentes. El núcleo de
> decisiones y las referencias de reglas incluidas son normativos; el manifiesto
> es su mapa para personas. La [matriz de capacidades](capabilities.md) distingue
> comportamiento implementado, inicial y de hoja de ruta.

Estándar de arquitectura ejecutable para proyectos creados y evolucionados por
agentes de programación.

Este repositorio no es una plantilla cerrada de carpetas. Reúne el protocolo y
las herramientas que un agente necesita para descubrir la arquitectura mínima
de un proyecto, materializarla con el conocimiento actual y protegerla mientras
el producto evoluciona.

## Objetivo principal

> Un agente debe poder crear, modificar y hacer evolucionar el proyecto de forma
> autónoma dentro de los límites decididos por el equipo. El repositorio debe
> proporcionarle suficiente contexto, políticas y validaciones para determinar
> qué puede hacer, dónde debe hacerlo y cómo demostrar que el resultado es
> conforme, sin solicitar intervención humana salvo cuando la petición requiera
> una decisión de producto, riesgo, ownership o autoridad que todavía no esté
> definida. Además, el repositorio debe organizar y proporcionar de forma
> eficiente, progresiva y trazable el contexto mínimo suficiente para cada
> tarea, de modo que el agente pueda localizar rápidamente el dominio,
> ownership, contratos, decisiones, dependencias, código y tests relevantes sin
> cargar información indiscriminada ni depender de memoria conversacional.

La autonomía es la conducta predeterminada. La intervención humana es una
escalada excepcional cuando el repositorio todavía no contiene autoridad
suficiente para tomar una decisión material; no es un paso ordinario del flujo
de desarrollo.

El acceso al contexto forma parte de la arquitectura: el repositorio ofrece un
punto de entrada pequeño y permite ampliar la información siguiendo ownership,
dependencias y evidencia concreta. Más contexto no es necesariamente mejor;
debe suministrarse el contexto relevante en el momento en que la tarea lo exige.

## Qué incluye

- [`MANIFESTO.md`](MANIFESTO.md): propósito, modelo de enforcement y mapa para
  personas.
- [`agent-core.md`](../../src/agentic_architecture_kit/data/norms/agent-core.md):
  contexto preventivo completo que lee el agente antes de decidir estructura.
- [`portable-rules.md`](../../src/agentic_architecture_kit/data/norms/portable-rules.md):
  normas del validador cargadas progresivamente mediante hallazgos.
- [`team-guide.md`](team-guide.md): guía humana para comprender, revisar y
  gobernar los artefactos creados por el kit.
- [`capabilities.md`](capabilities.md): matriz honesta de implementación y hoja
  de ruta de las herramientas de referencia.
- [`github-governance.md`](github-governance.md): controles requeridos de
  CODEOWNERS, revisión y protección de rama que no pueden demostrarse localmente.
- [`releasing.md`](releasing.md): procedimiento de release y publicación segura
  en PyPI para mantenedores.
- [`create-project-from-zero.md`](create-project-from-zero.md):
  versión web del procedimiento incluido como `aak guide bootstrap`.
- [`src/agentic_architecture_kit/`](../../src/agentic_architecture_kit/):
  distribución Python versionada con CLI, guías operativas, reglas portables,
  schemas, plantillas y adaptadores tecnológicos incluidos.
- [`tests/`](../../tests/): suite de conformidad de la distribución.
- [`examples/`](../../examples/): repositorios consumidores que ejercitan las
  reglas instaladas sin vendorizar la implementación.

## Cómo usarlo para crear un proyecto

1. Da al agente acceso de escritura al directorio del proyecto destino y acceso
   al registro del package, o proporciona un export offline de la versión fijada.
2. Proporciónale el objetivo, requisitos y restricciones conocidos del producto.
3. Pídele que ejecute `aak core` y `aak guide bootstrap` desde esa versión y lea
   ambos por completo antes de inicializar o realizar la primera modificación.
4. El agente descubre capacidades, hosts y límites actuales antes de crear
   estructura.
5. Fija y ejecuta una versión publicada del kit sin copiar su
   implementación al proyecto.
6. Adapta las plantillas para declarar la arquitectura específica del proyecto.
7. Ejecuta el build y los tests del proyecto y valida su arquitectura
   resultante.

Prompt inicial recomendado:

```text
Usa Agentic Architecture Kit para crear la arquitectura mínima justificable de
este proyecto. Ejecuta aak core y aak guide bootstrap desde la distribución
fijada y lee ambos por completo antes de inicializar o modificar por primera vez.
No copies una estructura de ejemplo mecánicamente: descubre capacidades, hosts,
límites y riesgos a partir de los requisitos y la evidencia actuales. Instala el
validador general sin redefinir sus reglas, crea la política específica del
proyecto y ejecuta el gate antes de crear estructura o implementación de
producto. En un repositorio existente, ejecútalo antes de la primera
modificación. Repítelo antes de declarar la tarea completa. Sigue la referencia
normativa de un hallazgo solo cuando sea necesaria; una referencia que no
resuelve es un fallo, nunca permiso para inferir la regla de memoria. Deja
explícitos los supuestos y las revisiones semánticas pendientes.
Trabaja autónomamente dentro de la autoridad declarada y escala únicamente una
decisión material de producto, riesgo, ownership o autoridad que no esté
definida.
```

## Distribución y payload propio del proyecto

El código portable, las guías operativas para el agente, los schemas, el catálogo
y las plantillas neutrales se publican juntos como `agentic-architecture-kit`.
El consumidor fija la versión exacta en `.agentic/toolchain.json` y la ejecuta
con `uvx` o `pipx`:

```bash
uvx --from agentic-architecture-kit==0.4.3 aak core
uvx --from agentic-architecture-kit==0.4.3 aak guide bootstrap
uvx --from agentic-architecture-kit==0.4.3 aak validate --fail-on-review
```

El agente no necesita acceso a este checkout fuente. La distribución fijada
contiene el núcleo preventivo, guías operativas, reglas, schemas, plantillas,
adaptadores y motor de validación necesarios para el bootstrap y la evolución
posterior.

En el repositorio consumidor solo viven decisiones y contexto propios:

```text
AGENTS.md
architecture/system-overview.md
architecture/decisions/
domain/global-invariants.md
.agentic/toolchain.json
.agentic/policies/architecture/project-policy.json
.agentic/policies/architecture/waivers.json
.agentic/policies/architecture/authorities.json
.agentic/policies/architecture/reviews.json
.github/CODEOWNERS
{raíz-real-del-módulo}/AGENTS.md
{raíz-real-del-módulo}/module.contract.yml
```

Solo se crean los elementos aplicables. No se añaden carpetas vacías,
abstracciones especulativas, módulos técnicos ni assemblies sin un límite actual
verificable.

Para entornos desconectados, `aak export-offline --output <directorio>` genera
una copia explícita y versionada con el mismo código, guías, schemas, reglas y
plantillas, además de un manifiesto SHA-256. Es una excepción operativa, no el
modelo de adopción predeterminado.

## Adoptar AAK en un proyecto existente

Ejecuta primero la simulación desde la raíz del repositorio existente, antes de
modificar el proyecto. El comando observa la estructura actual de Python o .NET
SDK-style y muestra cada archivo que añadiría, la política propuesta, la
integración de CI, el resultado de validación y el trabajo semántico que aún
necesita una decisión real:

```bash
uvx --from agentic-architecture-kit==0.4.3 aak adopt \
  --root . \
  --codeowner @tu-org/architecture \
  --ci github \
  --dry-run
```

Revisa el plan JSON y aplica después el mismo comando sin `--dry-run`:

```bash
uvx --from agentic-architecture-kit==0.4.3 aak adopt \
  --root . \
  --codeowner @tu-org/architecture \
  --ci github
```

En un repositorio con un único responsable, añade
`--authority-mode solo-maintainer` y usa ese mantenedor como `--codeowner`.
`aak adopt` rechaza un worktree con cambios salvo que se indique
`--allow-dirty`. Conserva los archivos y workflows existentes, así que puede
repetirse con seguridad; si un workflow existente no contiene el gate de AAK,
lo señala para integración en vez de sobrescribirlo.

El comando automatiza el bootstrap mecánico: registros de gobernanza, propuesta
de política observada, gate opcional de GitHub Actions, validación estricta e
índice de contexto. Termina con código distinto de cero cuando quedan problemas
de conformidad o trabajo semántico y los enumera en `requiredActions`. Nunca
inventa contratos de módulo, contenido local de `AGENTS.md`, waivers ni
aprobaciones semánticas. Completa esos elementos con conocimiento real del
proyecto, ejecuta su build y sus tests y repite
`aak validate --fail-on-review` antes del merge.

## Verificar el kit

Requiere Python 3.9 o posterior y no instala dependencias de terceros.

```bash
python3 -m pip install --no-deps -e .
python3 -m unittest discover -s tests -v
aak --help
aak validate --fail-on-review
aak core
aak guide
aak guide bootstrap
aak guide github-governance
aak template
aak template AGENTS.md
aak adopt --help
aak explain DEP001
aak context index
aak context locate "architecture validation"
aak validate --root examples/dotnet-valid
```

Para una inicialización de bajo nivel o de un proyecto nuevo, `aak init` crea
los archivos de gobernanza y escribe una propuesta observada de
`project-policy.json` sin ejecutar el flujo completo de adopción:

```bash
uvx --from agentic-architecture-kit==0.4.3 aak init --root . --codeowner @tu-org/architecture
```

Para un repositorio mantenido por una sola persona, declara esa restricción de
forma honesta en lugar de configurar una auto-review imposible:

```bash
uvx --from agentic-architecture-kit==0.4.3 aak init --root . \
  --codeowner @tu-usuario --authority-mode solo-maintainer
```

Las revisiones `solo-maintainer` usan una URL durable de atestación del
mantenedor en GitHub. No afirman que aprobar el propio pull request sea una
revisión independiente.

En un repositorio vacío, indica la tecnología conocida con `--adapter dotnet` o
`--adapter python`. La propuesta observada es un punto de partida, no una
aprobación de todos los límites encontrados: hay que revisarla y eliminar la
estructura accidental o injustificada antes de implementar.

La implementación de referencia soporta proyectos .NET SDK-style y Python.
Consulta
[`examples/dotnet-valid/`](../../examples/dotnet-valid/) para un repositorio
conforme y [`examples/dotnet-invalid/`](../../examples/dotnet-invalid/) para un
fallo arquitectónico intencional a nivel de código fuente.

El ejemplo inválido usa un único assembly para demostrar que la regla no depende
de haber fragmentado antes el proyecto.

## Licencia

Agentic Architecture Kit se distribuye bajo la
[Apache License 2.0](../../LICENSE) (`Apache-2.0`).
