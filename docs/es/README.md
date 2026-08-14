# Agentic Architecture Kit

[English — canonical](../../README.md) · [Política lingüística](language-policy.md)

> **Estado de implementación:** preview 0.4. El núcleo de decisiones y las
> referencias de reglas incluidas en el paquete son normativos; el manifiesto es
> su mapa para personas. La
> [matriz de capacidades](capabilities.md) distingue comportamiento implementado,
> inicial y de hoja de ruta.

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
  procedimiento operativo que debe seguir el agente.
- [`src/agentic_architecture_kit/`](../../src/agentic_architecture_kit/):
  distribución Python versionada con CLI, reglas portables, schemas, plantillas
  y adaptadores tecnológicos incluidos.
- [`tests/`](../../tests/): suite de conformidad de la distribución.
- [`examples/`](../../examples/): repositorios consumidores que ejercitan las
  reglas instaladas sin vendorizar la implementación.

## Cómo usarlo para crear un proyecto

1. Da al agente acceso a este repositorio y al directorio del nuevo proyecto.
2. Proporciónale el objetivo, requisitos y restricciones conocidos del producto.
3. Pídele que ejecute `aak core`, lea completamente el núcleo de decisiones y use
   `docs/create-project-from-zero.md` para la inicialización.
4. El agente descubre capacidades, hosts y límites actuales antes de crear
   estructura.
5. Fija y ejecuta una versión publicada del validador sin copiar su
   implementación al proyecto.
6. Adapta las plantillas para declarar la arquitectura específica del proyecto.
7. Ejecuta los tests del validador y la validación arquitectónica del proyecto.

Prompt inicial recomendado:

```text
Usa Agentic Architecture Kit para crear la arquitectura mínima justificable de
este proyecto. Ejecuta aak core, lee por completo el núcleo de decisiones y usa
docs/create-project-from-zero.md para inicializarlo.
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

El código portable, los schemas, el catálogo y las plantillas neutrales se
publican juntos como `agentic-architecture-kit`. El consumidor fija la versión
exacta en `.agentic/toolchain.json` y la ejecuta con `uvx` o `pipx`:

```bash
uvx --from agentic-architecture-kit==0.4.0 aak validate --fail-on-review
```

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
una copia explícita y versionada con manifiesto SHA-256. Es una excepción
operativa, no el modelo de adopción predeterminado.

## Verificar el kit

Requiere Python 3.9 o posterior y no instala dependencias de terceros.

```bash
python3 -m pip install --no-deps -e .
python3 -m unittest discover -s tests -v
aak --help
aak validate --fail-on-review
aak core
aak explain DEP001
aak context index
aak context locate "architecture validation"
aak validate --root examples/dotnet-valid
```

Para inicializar la gobernanza en un proyecto existente y dejar que el agente
descubra y escriba después su policy:

```bash
uvx --from agentic-architecture-kit==0.4.0 aak init --root . --codeowner @tu-org/architecture
```

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
