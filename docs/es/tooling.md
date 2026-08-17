# Herramientas y distribución de arquitectura

[English — canonical](../tooling.md)

La implementación de referencia se publica como la distribución Python
versionada `agentic-architecture-kit`. El package mantiene separados siete
aspectos:

1. la semántica portable, referencias normativas y el motor;
2. el núcleo de decisiones y contratos JSON incluidos;
3. la arquitectura propia en `project-policy.json`;
4. licencias y revisiones semánticas ligadas a huella;
5. autoridad y controles externos declarados;
6. adaptadores de observación incluidos o suministrados por plugins;
7. guías operativas versionadas y plantillas neutrales expuestas mediante
   comandos públicos de la CLI.

Requiere Python 3.9 o posterior y no tiene dependencias runtime de terceros. Los
adaptadores incluidos soportan repositorios .NET SDK-style y packages Python.

## Instalación del consumidor

El consumidor mantiene `.agentic/toolchain.json`, con versiones exactas de
distribución, catálogo y extensiones:

```json
{
  "version": 1,
  "distribution": "agentic-architecture-kit",
  "toolVersion": "0.4.5",
  "catalogVersion": 2,
  "extensions": []
}
```

La versión se ejecuta sin instalación global:

```bash
uvx --from agentic-architecture-kit==0.4.5 aak validate --fail-on-review
uvx --from agentic-architecture-kit==0.4.5 aak context locate "order lifecycle"
```

La misma distribución contiene todo lo necesario para que un agente inicialice
un proyecto nuevo o incorpore un repositorio existente a la gobernanza; no
necesita acceso al repositorio fuente:

```bash
aak core
aak guide bootstrap
aak guide github-governance
aak template
aak template AGENTS.md
```

`aak` rechaza validación y contexto si la herramienta, el catálogo o una
extensión instalada no coinciden con los pins. Un upgrade es así un cambio
explícito y revisable.

`aak init --root . --codeowner @equipo/arquitectura` crea solo gobernanza propia
y una entrada CODEOWNERS. También pide al adaptador seleccionado que observe el
repositorio y escribe una propuesta de `project-policy.json` con los módulos,
hosts, proyectos, patrones de namespace declarados en fuentes y referencias
exactas que ha encontrado. En .NET, los namespaces y `RootNamespace` son
evidencia; `AssemblyName` no se trata como namespace. Es andamiaje factual: el
agente o el equipo elimina los límites accidentales o injustificados, sin tratar
la observación como aprobación arquitectónica.

`aak adopt --root . --codeowner @equipo/arquitectura --ci github` orquesta la
adopción de un repositorio existente. Ejecuta la inicialización, añade
opcionalmente el gate de GitHub Actions incluido, crea el índice de contexto,
ejecuta la validación estricta y devuelve un único informe JSON con las acciones
posteriores explícitas. `--dry-run` genera un plan sin escrituras. El comando
conserva los archivos existentes, rechaza un worktree con cambios salvo que
`--allow-dirty` sea explícito y nunca inventa contratos semánticos, waivers ni
aprobaciones.

El adaptador se selecciona automáticamente si ya hay `.csproj`,
`pyproject.toml` o código Python. Antes de que existan artefactos tecnológicos,
se indica `--adapter dotnet` o `--adapter python`; la policy generada mantiene
arrays arquitectónicos vacíos y válidos hasta incorporar código de producto.

## Validación y contexto

```bash
aak validate --format json
aak validate --base-ref origin/main --fail-on-review
aak validate --task-id TASK-123
aak core
aak guide bootstrap
aak guide github-governance
aak template AGENTS.md
aak explain DEP001
aak context index
aak context locate "order lifecycle"
aak context references CreateOrder
aak context tests CreateOrder
aak context impact src/Modules/Orders
```

`FAIL` devuelve 1. Con `--fail-on-review`, un `REVIEW_REQUIRED` pendiente también
devuelve 1. La configuración inválida o un pin incompatible devuelve 2. Cada
resultado incluye digests canónicos de toolchain, policy, licencias, reviews,
autoridades, catálogo y observación.

Cada hallazgo contiene `reference` normativa resoluble y `ruleDigest`.
`aak explain` combina la definición con estado actual, scopes, evidencia y
waiver o review aplicado. Una referencia ausente hace fallar la validación.

Cada waiver y review semántico debe persistir ese `ruleDigest` exacto. Un digest
válido pero distinto degrada la licencia a `REVIEW_REQUIRED` e impide aplicarla
a la semántica actual de la regla.

## Extensiones tecnológicas

Los adaptadores externos usan el grupo de entry points
`agentic_architecture_kit.adapters` y se fijan en `toolchain.json`:

```toml
[project.entry-points."agentic_architecture_kit.adapters"]
rust = "my_aak_rust_adapter:observe"
```

Un adaptador observa hechos; no redefine reglas portables. Las comprobaciones
semánticas específicas permanecen en los tests arquitectónicos del consumidor.

## Exportación offline

Para un entorno aislado:

```bash
aak export-offline --output ./offline
```

Se genera `agentic-architecture-kit-{versión}/` con
`OFFLINE-MANIFEST.json` y SHA-256 de cada archivo. El payload contiene las mismas
guías operativas y plantillas que el wheel instalado. La exportación conserva su
identidad de versión y debe sustituirse completa, no editarse como fork oculto.

Los límites semánticos y el subconjunto soportado de JSON Schema/YAML se detallan
en la [documentación canónica](../tooling.md) y en la
[matriz de capacidades](capabilities.md).
