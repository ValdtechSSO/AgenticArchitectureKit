# Agentic Architecture Kit

[English — canonical](../../README.md) · [Política lingüística](language-policy.md)

> **Estado de implementación:** preview 0.2. El manifiesto es normativo; la
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

- [`MANIFESTO.md`](MANIFESTO.md): reglas normativas de inicialización, evolución
  y conformidad.
- [`team-guide.md`](team-guide.md): guía humana para comprender, revisar y
  gobernar los artefactos creados por el kit.
- [`capabilities.md`](capabilities.md): matriz honesta de implementación y hoja
  de ruta de las herramientas de referencia.
- [`github-governance.md`](github-governance.md): controles requeridos de
  CODEOWNERS, revisión y protección de rama que no pueden demostrarse localmente.
- [`create-project-from-zero.md`](create-project-from-zero.md):
  procedimiento operativo que debe seguir el agente.
- [`tools/architecture/`](../../tools/architecture/): validador portable, catálogo de
  reglas, adaptadores tecnológicos y tests de conformidad.
- [`.agentic/contracts/schemas/`](../../.agentic/contracts/schemas/): contratos de la
  policy, los waivers, las autoridades, las revisiones semánticas, el resultado
  y los módulos.
- [`.agentic/templates/project/`](../../.agentic/templates/project/): plantillas para
  materializar únicamente las decisiones aplicables al proyecto.

## Cómo usarlo para crear un proyecto

1. Da al agente acceso a este repositorio y al directorio del nuevo proyecto.
2. Proporciónale el objetivo, requisitos y restricciones conocidos del producto.
3. Pídele que lea primero `MANIFESTO.md` y
   `docs/create-project-from-zero.md`.
4. El agente descubre capacidades, hosts y límites actuales antes de crear
   estructura.
5. Copia el validador y los schemas sin modificar su semántica general.
6. Adapta las plantillas para declarar la arquitectura específica del proyecto.
7. Ejecuta los tests del validador y la validación arquitectónica del proyecto.

Prompt inicial recomendado:

```text
Usa Agentic Architecture Kit para crear la arquitectura mínima justificable de
este proyecto. Lee MANIFESTO.md y docs/create-project-from-zero.md por completo.
No copies una estructura de ejemplo mecánicamente: descubre capacidades, hosts,
límites y riesgos a partir de los requisitos y la evidencia actuales. Instala el
validador general sin redefinir sus reglas, crea la política específica del
proyecto y deja explícitos los supuestos y las revisiones semánticas pendientes.
Trabaja autónomamente dentro de la autoridad declarada y escala únicamente una
decisión material de producto, riesgo, ownership o autoridad que no esté
definida.
```

## Payload que recibe el proyecto

El agente copia sin reinterpretar:

```text
tools/architecture/
tools/scripts/validate-architecture.sh
.agentic/contracts/schemas/
```

Después genera para ese proyecto:

```text
AGENTS.md
architecture/system-overview.md
architecture/decisions/
domain/global-invariants.md
src/Modules/{CurrentModule}/AGENTS.md
src/Modules/{CurrentModule}/module.contract.yml
.agentic/policies/architecture/project-policy.json
.agentic/policies/architecture/waivers.json
.agentic/policies/architecture/authorities.json
.agentic/policies/architecture/reviews.json
.github/CODEOWNERS
```

Solo se crean los elementos aplicables. No se añaden carpetas vacías,
abstracciones especulativas, módulos técnicos ni assemblies sin un límite actual
verificable.

## Verificar el kit

Requiere Python 3.9 o posterior y no instala dependencias de terceros.

```bash
python3 -m unittest discover -s tools/architecture/tests -v
python3 tools/architecture/validate.py --help
python3 tools/architecture/validate.py --fail-on-review
python3 tools/architecture/context.py index
python3 tools/architecture/context.py locate "architecture validation"
python3 tools/architecture/validate.py --root examples/dotnet-valid
```

Una vez instalado en un proyecto:

```bash
./tools/scripts/validate-architecture.sh
./tools/scripts/validate-architecture.sh --format json
./tools/scripts/validate-architecture.sh --fail-on-review
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
