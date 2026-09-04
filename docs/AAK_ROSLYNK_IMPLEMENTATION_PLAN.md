# Plan de implementación: integración de Agentic Architecture Kit con Roslynk

> **Destinatario:** agente de implementación Codex  
> **Repositorio principal:** `ValdtechSSO/AgenticArchitectureKit`  
> **Línea base inspeccionada:** AAK `0.4.9`, commit `2d93cb4022abb22c3b5570555c0fa488d7de64c9`  
> **Proveedor semántico considerado:** `mrpmorris/Roslynk`, release `1.1.0`, commit de referencia `404b19c96faed0b0c864ca2312a08383ecc1d970`  
> **Fecha del plan:** 2026-09-04

---

## 1. Mandato para Codex

Implementa en AAK una integración con inteligencia semántica de C# que sea:

- **opcional** para proyectos que no usan .NET o no tienen Roslynk;
- **provider-neutral** dentro del núcleo de AAK;
- **Roslynk-aware** en la experiencia del agente;
- **determinista y revision-bound** cuando sus resultados se usen como evidencia de arquitectura;
- **read-only** desde la perspectiva de observación arquitectónica;
- compatible con la política existente, los adapters, los digests, la comparación con `--base-ref`, los artefactos de evidencia y `--fail-on-review`;
- explícita respecto a degradación, cobertura parcial, resultados truncados y ausencia del proveedor.

No conviertas Roslynk en una dependencia obligatoria de `agentic-architecture-kit`. No copies su código dentro de AAK y no introduzcas una dependencia de .NET 10 para usuarios de Python, otros lenguajes o proyectos .NET que no hayan habilitado observación semántica.

Antes de modificar archivos:

```bash
python3 -m pip install --no-deps -e .
aak core
aak guide implement-change
aak guide adapter-development
aak validate --fail-on-review
```

Lee también:

```text
AGENTS.md
README.md
docs/capabilities.md
docs/language-policy.md
docs/adapter-development.md
src/agentic_architecture_kit/data/norms/agent-core.md
src/agentic_architecture_kit/data/norms/portable-rules.md
src/agentic_architecture_kit/data/guides/implement-change-prompt.md
src/agentic_architecture_kit/adapters/dotnet.py
src/agentic_architecture_kit/context.py
src/agentic_architecture_kit/model.py
```

Descubre el siguiente identificador ADR disponible. No inventes un número fijo a partir de este documento.

---

## 2. Problema que se quiere resolver

AAK dispone hoy de dos mecanismos relacionados con código fuente .NET:

1. El adapter .NET observa proyectos SDK, `ProjectReference`, namespaces declarados y directivas `using`.
2. `aak context symbol`, `references` y `tests` hacen búsqueda textual exacta.

Estos mecanismos son útiles, pero no equivalen a un modelo semántico del compilador.

En particular, una directiva C#:

```csharp
using Payments.Infrastructure;
```

no demuestra que el archivo utilice realmente un símbolo de ese namespace. Puede ser un `using` no usado. Al mismo tiempo, una dependencia real puede existir sin directiva `using`:

```csharp
var gateway = new global::Payments.Infrastructure.StripeGateway();
```

También existen aliases, `global using`, partial classes, código generado, Razor, múltiples target frameworks y ramas condicionales. Una búsqueda textual puede confundir comentarios, strings o símbolos homónimos.

Roslynk proporciona al agente acceso MCP al modelo semántico de Roslyn: símbolos, definiciones, referencias, callers, implementaciones, jerarquías, diagnósticos y otras operaciones. Esto mejora de inmediato la investigación del agente, pero la API actual de Roslynk está orientada a consultas interactivas y devuelve outlines compactos. No debe asumirse que esas consultas aisladas constituyen por sí solas una exportación completa, estable y no truncada del grafo de dependencias de una solución.

La integración debe resolver ambos usos sin mezclarlos:

- **inteligencia interactiva para el agente** durante investigación e implementación;
- **evidencia semántica determinista** para índices, reglas y CI.

---

## 3. Decisión arquitectónica obligatoria

Implementar una arquitectura de **dos planos**.

### 3.1. Plano interactivo del agente

El agente usa Roslynk directamente mediante MCP para:

- abrir la solución;
- navegar símbolos;
- buscar referencias reales;
- identificar callers e implementaciones;
- consultar jerarquías;
- obtener diagnósticos rápidos durante el ciclo de edición.

AAK proporciona las reglas operativas para usarlo correctamente, pero no envuelve cada herramienta Roslynk con un comando equivalente.

### 3.2. Plano de evidencia de AAK

AAK acepta una **observación semántica versionada, completa y ligada al estado exacto del workspace** mediante un contrato provider-neutral.

Esta observación sólo debe influir en `aak validate`, índices y evidencia cuando:

- el proveedor está identificado y versionado;
- los inputs están fingerprinted;
- la cobertura está declarada;
- no existe truncación oculta;
- los paths son relativos y permanecen dentro del repositorio;
- AAK puede diferenciar cobertura completa, parcial, no disponible y no aplicable.

El bridge real hacia Roslynk debe vivir en una distribución separada, por ejemplo:

```text
aak-dotnet-roslynk
```

El núcleo de AAK no debe depender de Roslynk ni de librerías MCP de terceros.

### 3.3. Autoridad

La responsabilidad queda separada así:

| Componente | Responsabilidad |
|---|---|
| AAK | Política, contratos, ownership, reglas, autoridad, validación, evidencia, fallback y diagnóstico arquitectónico |
| Roslynk | Resolución semántica C#/Razor mediante Roslyn y diagnósticos del compilador |
| Bridge externo | Convertir observación de Roslynk al contrato estable de AAK sin decidir arquitectura |
| Agente | Investigar, implementar y corregir dentro de la autoridad declarada |
| Git | Revisión, baseline, cambios y trazabilidad |

**Roslynk informa qué hace el código. AAK decide si eso está permitido.**

---

## 4. Alcance

### 4.1. Debe implementarse en AAK

1. Guía versionada para inteligencia semántica y uso de Roslynk por agentes.
2. Integración de esa guía con `implement-change` y la plantilla `AGENTS.md`.
3. Contrato provider-neutral para observación semántica de dependencias de código.
4. Carga de proveedores externos mediante entry points.
5. Configuración explícita de modo advisory o required.
6. Modelo de cobertura, provenance, resolución semántica, fingerprints y degradación.
7. Merge seguro entre observación estructural/sintáctica y observación semántica.
8. Uso de observación combinada por `aak validate` y `aak context index`.
9. Regla para impedir que una observación semántica requerida falte, esté obsoleta o sea incompleta sin quedar visible.
10. Pruebas con un proveedor falso; el CI del núcleo de AAK no debe requerir Roslynk.
11. Documentación canónica en inglés y traducciones españolas exigidas por la política del repositorio.
12. Actualización honesta de la matriz de capacidades.

### 4.2. Debe implementarse fuera del núcleo de AAK

1. La distribución `aak-dotnet-roslynk`.
2. El bridge MCP o sidecar .NET que obtiene la instantánea semántica.
3. Pruebas de integración reales contra Roslynk y .NET 10.
4. Cualquier cambio upstream necesario en Roslynk para exportación masiva estable.

### 4.3. No objetivos

No implementar en esta iniciativa:

- un language server nuevo;
- un reemplazo de Roslynk;
- un wrapper AAK para todas las herramientas MCP de Roslynk;
- edición de código desde `aak validate`;
- instalación automática de Roslynk;
- escritura automática de configuraciones privadas del editor o del harness;
- envío de código a servicios externos;
- sustitución de `dotnet build`, `dotnet test`, integration tests o Playwright por `get_diagnostics`;
- autorización de dependencias a partir de observación;
- almacenamiento de un grafo de símbolos completo cuando sólo se necesitan edges arquitectónicos;
- parsing de outlines para LLM como contrato estable de CI;
- creación automática de una `.sln` o `.slnx` sólo para satisfacer al proveedor.

---

## 5. Invariantes de diseño

La implementación no está completa si viola cualquiera de estas condiciones.

### INV-SEM-001 — AAK continúa funcionando sin Roslynk

Todos los comandos existentes deben conservar su funcionamiento cuando no exista configuración semántica.

### INV-SEM-002 — No hay PASS silencioso por ausencia de evidencia requerida

Cuando el proyecto declara observación semántica `required`, ausencia, cobertura parcial, snapshot obsoleto o truncación impiden completar en verde con `--fail-on-review`.

### INV-SEM-003 — La observación no concede permiso

Un edge observado nunca modifica automáticamente `allowedProjectDependencies`, `dependencyRules`, módulos, hosts o contratos.

### INV-SEM-004 — El bridge es read-only

El contrato de AAK sólo permite observación. No debe exponer `apply_patch`, rename, code actions ni otra mutación como parte de validación o indexación.

### INV-SEM-005 — No se ocultan archivos sin cobertura

Un proveedor puede sustituir candidatos sintácticos únicamente para archivos que declare como completamente observados. En archivos no cubiertos se conserva la observación base.

### INV-SEM-006 — No se acepta truncación como cobertura completa

Si el proveedor o Roslynk indica `truncated=true`, límites alcanzados o resultados parciales, la cobertura no puede ser `complete`.

### INV-SEM-007 — Evidencia ligada al workspace exacto

La observación incluye hashes de los inputs relevantes. Un cambio de contenido invalida la instantánea aunque el commit SHA sea el mismo y el worktree esté dirty.

### INV-SEM-008 — Paths seguros y reproducibles

No se persisten paths absolutos. Todo path del repositorio es POSIX, relativo al root, resoluble dentro de éste y validado contra escape mediante `..` o symlinks.

### INV-SEM-009 — Fallback explícito

Cuando se usa la observación sintáctica/textual por falta de semántica, el resultado debe declarar provider, resolución y razón de degradación.

### INV-SEM-010 — Build y test siguen siendo autoridad de finalización

Los diagnósticos Roslynk aceleran el loop del agente, pero la finalización exige los comandos reales del proyecto más `aak validate`.

### INV-SEM-011 — AAK conserva su distribución ligera

El paquete principal sigue siendo Python 3.9+ y no añade una dependencia runtime de MCP, Roslyn o .NET.

### INV-SEM-012 — Cambios de enforcement quedan gobernados

Eliminar un requisito semántico, reducirlo de `required` a `advisory` o reducir su scope debe detectarse como reducción de enforcement en la comparación con base.

---

## 6. Arquitectura objetivo

```text
                         CODING AGENT
                              |
             +----------------+----------------+
             |                                 |
             v                                 v
       AAK operational guide             Roslynk MCP
       + policy + contracts              interactive/live
             |                                 |
             |                                 +-- symbols
             |                                 +-- references
             |                                 +-- callers
             |                                 +-- implementations
             |                                 +-- hierarchy
             |                                 +-- diagnostics
             |
             v
      AAK structural adapter
             |
             +-- projects
             +-- project references
             +-- declared namespaces
             +-- syntactic candidates
             |
             v
  provider-neutral semantic observer contract
             ^
             |
      aak-dotnet-roslynk extension
             ^
             |
     deterministic Roslynk export
             |
             v
      merge + coverage validation
             |
             +-- aak validate
             +-- aak context index
             +-- task evidence/digests
             +-- base comparison
```

No debe existir una dependencia directa:

```text
agentic-architecture-kit -> Roslynk
```

La relación debe ser:

```text
agentic-architecture-kit <- stable contract <- external extension -> Roslynk
```

---

## 7. Estrategia de entrega

Separar el trabajo en cuatro changesets. No mezclar la integración documental de bajo riesgo con el enforcement semántico completo en un único cambio difícil de revisar.

### Changeset A — Integración inmediata del agente

Puede completarse sin cambios en Roslynk y sin nueva dependencia runtime.

### Changeset B — Contrato y núcleo provider-neutral

Se implementa en AAK con un fake provider y fixtures deterministas.

### Changeset C — Bridge real `aak-dotnet-roslynk`

Distribución separada. Está condicionado a disponer de una exportación completa y machine-readable.

### Changeset D — Activación inicial de enforcement semántico

Conecta el bridge real, ejemplos, CI opcional y cambia la capability correspondiente de roadmap a initial/implemented según la evidencia real.

El orden es obligatorio: **A → B → C → D**.

---

# CHANGESET A — Integración inmediata del agente

## 8. ADR de integración

Crear un ADR cuyo título sea equivalente a:

```text
Semantic code intelligence is advisory to agents and evidence-bound for validation
```

Debe registrar:

- la arquitectura de dos planos;
- por qué Roslynk no es dependencia obligatoria de AAK;
- por qué AAK no debe envolver todas las herramientas Roslynk;
- por qué un daemon vivo no es suficiente como evidencia de CI;
- por qué los resultados usados para validar deben estar fingerprinted;
- que AAK conserva autoridad sobre políticas y permisos;
- que la integración de observación es read-only;
- que `dotnet build` y tests reales siguen siendo obligatorios;
- alternativas rechazadas:
  - reemplazar el adapter .NET por llamadas live MCP;
  - parsear outlines de herramientas individuales;
  - copiar/forkear Roslynk dentro de AAK;
  - tratar `using` como equivalente permanente a una referencia semántica.

Actualizar las referencias arquitectónicas de AAK siguiendo `aak guide architecture-context-authoring-prompt`.

## 9. Nueva guía versionada

Crear:

```text
src/agentic_architecture_kit/data/guides/semantic-code-intelligence.md
```

Registrar en:

```text
src/agentic_architecture_kit/guide_cli.py
```

Comando resultante:

```bash
aak guide semantic-code-intelligence
```

La guía debe ser provider-neutral en sus reglas y contener una sección concreta de Roslynk para proyectos .NET.

### 9.1. Contenido mínimo de la guía

#### Separación de responsabilidades

```text
AAK: architectural authority and conformance
Roslynk: compiler-semantic discovery
Git/build/tests: state and executable proof
```

#### Flujo recomendado para .NET

```text
1. Run the AAK preflight and locate the owning module.
2. Discover the applicable solution path; do not create one speculatively.
3. If Roslynk is available, call open_solution once.
4. Wait for ready status; Indexing is not permission to fall back silently.
5. Use semantic navigation for symbols, references, callers, implementations and hierarchy.
6. Record whether evidence is semantic, syntactic, textual, inferred or unknown.
7. Implement the smallest authorized change.
8. Use get_diagnostics during the edit loop.
9. Run real build, tests and AAK validation before completion.
```

#### Herramientas Roslynk recomendadas

La guía puede nombrar, sin copiar toda la documentación upstream:

```text
open_solution
get_solution_status
search_symbols
get_symbol
get_members
find_definition
find_references
get_callers
find_implementations
get_type_hierarchy
get_diagnostics
```

#### Reglas de seguridad

- La guía de AAK depende sólo de herramientas read-only.
- Nunca deducir permiso arquitectónico de un resultado Roslynk.
- No usar `reload_solution` por iniciativa propia si el file watcher mantiene el modelo.
- No confundir `get_diagnostics` con build/test completos.
- Tratar `Indexing`, `Ambiguous`, `NotFound`, `Stale`, `Conflict` y `truncated` como estados explícitos.
- No persistir paths locales absolutos en artefactos del repositorio.
- No enviar secretos ni contenido fuera del host; la integración prevista es local/loopback.

#### Fallback

Cuando Roslynk no esté disponible:

- usar el adapter y los comandos contextuales existentes;
- etiquetar la evidencia como sintáctica o textual;
- no afirmar que se verificaron referencias semánticas;
- si la tarea requiere exactitud semántica para una decisión material, clasificar el caso como `TECHNOLOGY_OBSERVATION_GAP`.

## 10. Integrar la guía con el workflow principal

Modificar:

```text
src/agentic_architecture_kit/data/guides/implement-change-prompt.md
```

### 10.1. Mandatory preflight

Añadir después de localizar el owner:

```text
For a language with configured semantic code intelligence, use it to resolve the
requested behavior's symbols, real references, implementations and direct
consumers before relying on textual search. Record the provider, coverage and
resolution level. Semantic observation does not authorize an architectural edge.
```

### 10.2. Change classification

Mantener `TECHNOLOGY_OBSERVATION_GAP` y aclarar que aplica cuando:

- AAK necesita demostrar un edge real, pero sólo dispone de candidates sintácticos;
- el proveedor requerido está ausente;
- una solución/configuración no puede cargarse completamente;
- existe truncación o cobertura parcial.

### 10.3. Implementation plan contract

Añadir un campo:

```text
Code-intelligence provider and evidence level: <PROVIDER|NONE> / <SEMANTIC|SYNTACTIC|TEXTUAL>
```

### 10.4. Validation loop

Incluir:

```text
Use compiler diagnostics for rapid local feedback when available, then run the
project's authoritative build and tests. A green semantic diagnostic query does
not replace build targets, generators, packaging, migrations, integration tests
or browser tests.
```

## 11. Actualizar la plantilla de proyecto

Modificar:

```text
src/agentic_architecture_kit/data/templates/project/AGENTS.md
```

Añadir una sección breve:

```markdown
## Code intelligence

- Use the configured semantic provider for compiler-resolved C# navigation when available.
- Use AAK for architecture authority and validation; semantic discovery never grants a dependency.
- Fall back explicitly to syntactic/textual evidence and report the reduced confidence.
- Run the real build and tests before completion.
```

No hardcodear que todos los proyectos usan Roslynk. La plantilla debe hablar de “configured semantic provider” y la guía explicará Roslynk como implementación .NET.

## 12. Documentación web

Crear o actualizar:

```text
docs/semantic-code-intelligence.md
docs/es/semantic-code-intelligence.md
README.md
docs/capabilities.md
docs/es/capabilities.md
docs/es/README.md                 # si contiene índice de navegación
```

Respetar `docs/language-policy.md`:

- inglés canónico;
- español equivalente;
- nombres de comandos, keys y tipos en inglés;
- no declarar una capacidad como implemented sólo por documentarla.

### Estado correcto tras Changeset A

Añadir una capability separada:

```text
Agent-side semantic discovery guidance — Implemented
```

Mantener todavía:

```text
Compiler-grade symbol graph — Roadmap
Semantic source-dependency enforcement — Roadmap
```

La documentación debe indicar que el agente puede usar Roslynk, pero AAK aún no consume una instantánea semántica como evidencia automática.

## 13. Pruebas del Changeset A

Añadir pruebas que demuestren:

1. `aak guide` lista `semantic-code-intelligence`.
2. `aak guide semantic-code-intelligence` devuelve el recurso empaquetado.
3. La guía contiene explícitamente la separación AAK/semantic provider.
4. La guía prohíbe sustituir build/tests por diagnostics.
5. La plantilla `AGENTS.md` no hace Roslynk obligatorio.
6. `implement-change` incluye provider y evidence level.
7. Los package data incluyen la nueva guía en la distribución construida.
8. La documentación inglesa y española requerida existe.

No uses sólo asserts de substrings triviales. Incluye al menos una prueba que construya o inspeccione el wheel/sdist o utilice el resource loader de la distribución instalada.

## 14. Definition of Done del Changeset A

- No cambia el resultado de las reglas existentes.
- No añade dependencia runtime.
- El workflow del agente sabe cuándo y cómo usar inteligencia semántica.
- El fallback queda explícito.
- La capability matrix sigue siendo honesta.
- Todas las pruebas y self-validation pasan.

---

# CHANGESET B — Contrato provider-neutral y núcleo de observación

## 15. Configuración de proyecto

Añadir una propiedad opcional y schema-validada al project policy:

```json
{
  "observation": {
    "semantic": {
      "provider": "roslynk",
      "mode": "advisory",
      "solution": "MyProduct.slnx",
      "capabilities": ["source-dependencies"]
    }
  }
}
```

### 15.1. Contrato de configuración

```text
observation.semantic.provider
```

- nombre de entry point;
- patrón: `[a-z][a-z0-9_]*`;
- no es nombre de distribución;
- la distribución que lo implementa debe estar pinneada en `toolchain.json.extensions`.

```text
observation.semantic.mode
```

Valores iniciales:

- `advisory`: se utiliza cuando está disponible; si no lo está, AAK conserva fallback y expone degradación sin fingir cobertura semántica;
- `required`: la finalización estricta exige evidencia completa y vigente.

No introducir `auto`: la selección implícita dificulta reproducibilidad.

```text
observation.semantic.solution
```

- path opcional relativo al repositorio;
- si falta, el proveedor puede autodetectar sólo cuando existe un candidato inequívoco;
- no crear solución automáticamente;
- múltiples soluciones sin selección producen estado ambiguo.

```text
observation.semantic.capabilities
```

En la primera versión sólo admitir:

```json
["source-dependencies"]
```

No diseñar anticipadamente un catálogo enorme.

### 15.2. Compatibilidad

La ausencia de `observation` conserva exactamente el comportamiento previo.

El schema de policy debe mantener backward compatibility con documentos version `1`, salvo que el repositorio tenga una política explícita de bump de schema. No incrementar el número por reflejo si la propiedad es opcional y compatible.

## 16. Nuevo contrato Python

Crear un package interno equivalente a:

```text
src/agentic_architecture_kit/semantic_observers/
    __init__.py
    contracts.py
    merge.py
    fingerprint.py
```

Los nombres concretos pueden variar si la arquitectura existente exige otra colocación, pero no mezclar el bridge Roslynk dentro de `adapters/dotnet.py`.

### 16.1. Entry-point group

Usar:

```toml
[project.entry-points."agentic_architecture_kit.semantic_observers"]
roslynk = "aak_dotnet_roslynk:observe"
```

El loader debe:

- validar el nombre;
- encontrar exactamente un provider;
- rechazar ausencia o ambigüedad de forma estructurada;
- comprobar que el retorno es del tipo contractual;
- no ejecutar un comando arbitrario procedente de JSON;
- no cargar providers no seleccionados por el proyecto;
- dejar que `load_toolchain` verifique la versión de la distribución pinneada.

### 16.2. Modelo mínimo

Añadir modelos frozen equivalentes a los siguientes. Adapta los nombres al estilo del repositorio.

```python
@dataclass(frozen=True)
class SourceLocation:
    path: str
    start_line: int
    start_column: int
    end_line: int
    end_column: int


@dataclass(frozen=True)
class ObservationInput:
    path: str
    sha256: str


@dataclass(frozen=True)
class CoverageExclusion:
    path: str
    reason: str


@dataclass(frozen=True)
class SemanticCoverage:
    status: str  # complete | partial | unavailable
    covered_source_files: tuple[str, ...]
    exclusions: tuple[CoverageExclusion, ...]
    configurations: tuple[str, ...]
    truncated: bool = False


@dataclass(frozen=True)
class SemanticObservation:
    provider: str
    provider_version: str
    capability: str
    repository_revision: str
    workspace_fingerprint: str
    subject_path: str | None
    inputs: tuple[ObservationInput, ...]
    coverage: SemanticCoverage
    source_dependencies: tuple[SourceDependency, ...]
    diagnostics: tuple[str, ...] = ()
```

No uses strings de diagnóstico como sustituto de estados estructurados en la implementación final. Es aceptable empezar con un tipo sencillo durante red-green-refactor, pero el contrato público debe acabar con códigos o categorías estables.

### 16.3. Extender `SourceDependency` de forma compatible

Añadir campos opcionales con defaults para no romper adapters existentes:

```python
resolution: str = "syntactic"
provider: str = "technology-adapter"
source_symbol: str | None = None
target_symbol: str | None = None
target_project_path: str | None = None
locations: tuple[SourceLocation, ...] = ()
configurations: tuple[str, ...] = ()
```

Valores iniciales de `resolution`:

```text
manifest
semantic
syntactic
textual
heuristic
```

No conviertas esta lista en una escala numérica genérica. Cada consumidor debe decidir qué niveles satisfacen su garantía.

### 16.4. Provenance

Toda serialización de dependencias debe incluir, cuando proceda:

```json
{
  "provider": "roslynk",
  "providerVersion": "1.1.0",
  "resolution": "semantic",
  "sourceSymbol": "Orders.Application.CreateOrderHandler.Handle",
  "targetSymbol": "Payments.Contracts.IPaymentGateway.ChargeAsync",
  "targetProjectPath": "src/Modules/Payments/Contracts/Payments.Contracts.csproj",
  "locations": [
    {
      "path": "src/Modules/Orders/CreateOrderHandler.cs",
      "startLine": 42,
      "startColumn": 17,
      "endLine": 42,
      "endColumn": 32
    }
  ]
}
```

La versión del provider puede vivir en metadata de la observación para evitar repetición, pero debe seguir siendo resoluble desde cada finding/evidence record.

## 17. Fingerprint de inputs

No confíes sólo en:

```text
<commit SHA>+dirty
```

El proveedor debe devolver el manifest exacto de inputs repository-local que utilizó. AAK debe:

1. validar que cada path está dentro del root;
2. recalcular SHA-256 sobre los bytes actuales;
3. ordenar por path;
4. construir un digest canónico del manifest;
5. compararlo con `workspace_fingerprint`;
6. rechazar o invalidar evidencia si algún archivo cambió.

Inputs típicos de .NET:

```text
*.sln
*.slnx
*.csproj
*.props
*.targets
Directory.Build.*
Directory.Packages.props
global.json
NuGet.Config relevante si el proveedor lo utiliza
*.cs
*.razor
*.cshtml
```

El proveedor debe declarar lo que realmente leyó, no una lista teórica fija.

Para inputs externos al repositorio —SDK, MSBuild, paquetes— registrar identidades/versiones de entorno sin persistir paths privados absolutos. Esa metadata no sustituye los hashes de los inputs del repositorio.

## 18. Observación base honesta

Modificar el adapter .NET para dejar claro que una directiva `using` es un candidato sintáctico, no una referencia resuelta por el compilador.

Resultado deseado equivalente a:

```python
SourceDependency(
    source_path=relative_source,
    source_namespace=source_namespace,
    target_namespace=target_namespace,
    kind="using-directive",
    confidence="exact-syntax",
    resolution="syntactic",
    provider="dotnet-adapter",
)
```

No es obligatorio cambiar `confidence` si existe riesgo de romper consumers externos; en ese caso añade `resolution="syntactic"` y documenta el significado. Lo importante es que el JSON no presente la directiva como edge compiler-resolved.

Python AST imports pueden conservar resolución `syntactic`, con su `kind` específico. `ProjectReference` sigue siendo `manifest` y exacto.

## 19. Algoritmo de merge

Implementar una función pura y cubierta por tests:

```python
merge_observations(
    structural: ObservedArchitecture,
    semantic: SemanticObservation | None,
    mode: str,
) -> MergedObservation
```

### 19.1. Reglas

1. Projects, modules, hosts, project references, source files y namespaces base continúan procediendo del technology adapter.
2. El semantic observer sólo puede aportar la capability declarada.
3. Para un source file con cobertura semántica `complete`:
   - eliminar de ese archivo únicamente los candidates de la misma capability y resolución inferior;
   - conservar edges semánticos reales;
   - conservar observaciones no sustituibles, como project references.
4. Para un archivo no cubierto:
   - conservar los candidates sintácticos;
   - registrar fallback y motivo.
5. Cobertura `partial` nunca autoriza sustitución global.
6. `truncated=true` fuerza cobertura no completa.
7. Dedupe canónico por identidad semántica, no sólo por texto:

```text
sourcePath
sourceNamespace
sourceSymbol
 targetNamespace
 targetSymbol
 targetProjectPath
 kind
 configurations
```

8. Ordenar determinísticamente todas las colecciones.
9. No descartar un edge porque su target owner sea desconocido. El validator debe mantenerlo visible y aplicar la semántica actual de review.
10. Un provider nunca puede borrar project references ni declaraciones estructurales.

### 19.2. Ejemplo: falso positivo eliminado

Código:

```csharp
using Conclave.Cli; // no usado
namespace Conclave.Planning;
```

Base adapter:

```text
Planning -> Conclave.Cli, syntactic candidate
```

Semantic observation completa:

```text
No actual symbol reference
```

Merged result:

```text
No source dependency edge
```

### 19.3. Ejemplo: falso negativo detectado

Código:

```csharp
namespace Conclave.Planning;

public sealed class Planner
{
    private readonly global::Conclave.Cli.ConsoleWriter _writer = new();
}
```

Base adapter:

```text
No using candidate
```

Semantic observation:

```text
Conclave.Planning.Planner -> Conclave.Cli.ConsoleWriter
```

Merged result:

```text
Semantic edge; DEP001 can fail with exact location
```

## 20. Regla `OBS001`

Añadir una portable rule con nombre equivalente a:

```text
OBS001 — Required observation evidence is current and complete
```

### 20.1. Semántica

| Estado | Condición |
|---|---|
| `NOT_APPLICABLE` | No existe configuración semántica |
| `PASS` | El provider configurado produjo evidencia válida; en advisory puede informar que la evidencia fue utilizada |
| `NOT_APPLICABLE` o `PASS` degradado documentado | Modo advisory y provider no disponible; el fallback está explícito |
| `REVIEW_REQUIRED` | Modo required y el provider está unavailable, ambiguous, unsupported, partial o truncated |
| `FAIL` | Evidencia malformada, path escape, hash incorrecto, snapshot stale, provider distinto al configurado o capability falsa |

En modo `required`, `aak validate --fail-on-review` no puede terminar en verde con `REVIEW_REQUIRED`.

### 20.2. Archivos normativos

Actualizar de forma atómica:

```text
src/agentic_architecture_kit/data/rules.json
src/agentic_architecture_kit/data/norms/portable-rules.md
cualquier clasificación normativa JSON usada por el validator
docs/capabilities.md y traducción
engine.py o el evaluator correspondiente
pruebas de cobertura de headings/DOC001
```

Añadir al menos una negative mutation test asociada a la nueva regla, siguiendo el criterio de self-validation del repositorio.

## 21. Protección frente a reducción de enforcement

Extender la comparación de policy/base para que `CHG001` detecte como reducción material:

- eliminar `observation.semantic` cuando era required;
- cambiar `required` a `advisory`;
- eliminar `source-dependencies` de capabilities;
- cambiar a una solución/scope que cubre menos proyectos o archivos;
- aceptar silenciosamente partial/truncated donde antes se exigía complete.

Un cambio de versión del provider pinneado en toolchain no es por sí solo un cambio de arquitectura, pero debe mantener integridad y pasar tests. Un cambio de provider puede requerir review si altera la garantía o cobertura.

## 22. Integración con engine y digests

El engine debe recibir la observación ya combinada y la metadata de capas. Evita que cada evaluator vuelva a cargar al provider.

Flujo recomendado:

```text
load toolchain
load policy
run structural adapter once
load semantic provider once, if configured
validate semantic contract and inputs
merge observations once
digest merged observation and layer metadata
build ValidationContext
evaluate rules
retain evidence
```

Añadir a `ObservedArchitecture.as_dict()` o a un envelope de observación:

```json
{
  "layers": [
    {
      "provider": "dotnet-adapter",
      "resolution": "structural+syntactic"
    },
    {
      "provider": "roslynk",
      "providerVersion": "1.1.0",
      "capability": "source-dependencies",
      "coverage": "complete",
      "workspaceFingerprint": "sha256:..."
    }
  ]
}
```

El digest debe cambiar cuando cambien:

- provider o versión;
- capability;
- inputs;
- cobertura;
- edges;
- exclusiones;
- configuración relevante.

## 23. Integración con `aak context`

### 23.1. Index

Modificar `build_index()` para usar la observación combinada y añadir a cada dependency:

```text
resolution
provider
sourceSymbol
targetSymbol
targetProjectPath
locations
configurations
```

Añadir metadata de cobertura al `repository.json` o a un nuevo índice `observations.json`.

Preferencia recomendada:

```text
INDEX_FILES = (..., "observations")
```

`observations.json` debe contener sólo metadata/digests/cobertura, no necesariamente todo el snapshot si éste es grande.

### 23.2. Nuevo comando de estado

Añadir:

```bash
aak context status
```

Salida JSON mínima:

```json
{
  "adapter": "dotnet",
  "semantic": {
    "configured": true,
    "provider": "roslynk",
    "mode": "required",
    "available": true,
    "capabilities": ["source-dependencies"],
    "coverage": "complete",
    "resolutionUsed": "semantic",
    "fallbackUsed": false,
    "workspaceFingerprint": "sha256:..."
  }
}
```

Cuando haya fallback:

```json
{
  "coverage": "unavailable",
  "resolutionUsed": "syntactic",
  "fallbackUsed": true,
  "reasonCode": "PROVIDER_NOT_INSTALLED"
}
```

### 23.3. No convertir AAK en proxy de Roslynk

Mantener las consultas generales de callers, hierarchy, code actions y diagnostics en Roslynk MCP. No añadir automáticamente:

```text
aak context callers
aak context hierarchy
aak context diagnostics
```

salvo que exista un caso de uso AAK concreto y un contrato estable. El objetivo de `aak context` es producir contexto mínimo de arquitectura con provenance, no duplicar un language service.

### 23.4. Búsqueda textual existente

`aak context symbol/references/tests` puede conservar su fallback actual. Debe indicar claramente:

```text
confidence=exact-text-match
resolution=textual
```

No anunciarlo como compiler-semantic. La guía indicará que el agente debe preferir Roslynk para navegación semántica.

## 24. Evidencia de tareas

Cuando se ejecute validación con `--task-id`, el manifest debe incluir:

- digest de la observación semántica;
- provider y versión;
- workspace fingerprint;
- status de cobertura;
- modo advisory/required;
- si hubo fallback;
- códigos de degradación;
- referencia al artefacto semántico retenido, si se conserva.

No guardar por defecto enormes payloads duplicados. Puede conservarse un artefacto único por fingerprint y referenciarlo desde múltiples tareas.

No persistir:

- paths absolutos del usuario;
- tokens MCP;
- variables de entorno sensibles;
- contenido de paquetes externos;
- logs sin redacción.

## 25. Manejo de errores

Definir códigos estables, al menos:

```text
PROVIDER_NOT_CONFIGURED
PROVIDER_NOT_INSTALLED
PROVIDER_AMBIGUOUS
PROVIDER_UNAVAILABLE
SUBJECT_NOT_FOUND
SUBJECT_AMBIGUOUS
INDEXING_INCOMPLETE
UNSUPPORTED_CONFIGURATION
PARTIAL_COVERAGE
TRUNCATED_RESULT
STALE_INPUT
INPUT_HASH_MISMATCH
PATH_ESCAPE
INVALID_PROVIDER_OUTPUT
CAPABILITY_NOT_PROVIDED
```

El output humano puede ser amigable, pero JSON y tests deben usar códigos.

No convertir automáticamente un error operacional transitorio en una afirmación semántica negativa. “No se pudo observar” no significa “no existe dependencia”.

## 26. Pruebas del Changeset B

Crear tests dedicados, preferiblemente en archivos separados del monolito actual cuando ello no viole una decisión existente:

```text
tests/test_semantic_observation.py
tests/test_semantic_merge.py
tests/test_semantic_policy.py
```

### 26.1. Loader y contrato

- provider name válido/inválido;
- cero, uno y múltiples entry points;
- distribución pinneada ausente;
- return type incorrecto;
- capability no proporcionada;
- output no determinista detectado donde sea comprobable;
- path fuera del root rechazado.

### 26.2. Fingerprints

- manifest ordenado produce digest estable;
- cambio de bytes invalida snapshot;
- worktree dirty queda ligado al contenido real;
- symlink/`..` no puede escapar;
- paths absolutos rechazados;
- duplicados rechazados o canonicalizados de forma definida.

### 26.3. Merge

- complete semantic coverage sustituye candidates sintácticos del mismo archivo;
- no sustituye project references;
- partial coverage conserva fallback;
- uncovered file conserva candidate;
- semantic edge sin `using` aparece;
- unused `using` desaparece sólo con complete coverage;
- edges duplicados se canonicalizan;
- mismo nombre textual, símbolo diferente, no se mezcla;
- target owner desconocido sigue visible;
- configuraciones/TFMs diferentes se conservan.

### 26.4. Reglas

- required + complete → `OBS001 PASS`;
- required + unavailable → `REVIEW_REQUIRED`;
- required + partial → `REVIEW_REQUIRED`;
- required + truncated → `REVIEW_REQUIRED`;
- stale/malformed → `FAIL`;
- advisory + unavailable → fallback explícito sin false semantic PASS;
- `--fail-on-review` falla cuando corresponde;
- downgrade required → advisory se detecta mediante base comparison;
- existing policies sin `observation` conservan resultados.

### 26.5. DEP001/DEP002

Fixture A:

```text
module file has unused using to host
semantic coverage complete with no actual edge
expected: no DEP001 false positive
```

Fixture B:

```text
module file has fully-qualified host symbol without using
semantic observation includes actual edge
expected: DEP001 FAIL with source and target symbol/location
```

Fixture C:

```text
cross-module actual symbol targets non-contract implementation
expected: DEP002 FAIL
```

Fixture D:

```text
cross-module actual symbol targets declared public contract
expected: DEP002 PASS
```

Fixture E:

```text
test project consumes host
expected: remains treated as verification consumer according to existing semantics
```

### 26.6. Context y evidencia

- `aak context status` reporta provider/cobertura/fallback;
- index contiene provenance semántico;
- task evidence contiene digest y fingerprint;
- output no contiene root absoluto;
- dos ejecuciones sobre mismos inputs producen JSON canónico equivalente.

### 26.7. Tests sin Roslynk real

El núcleo de AAK debe usar un fake semantic observer instalado o inyectado para tests. El test suite principal no descarga herramientas, no usa red y no requiere .NET 10.

## 27. Definition of Done del Changeset B

- Existe contrato público y documentado de semantic observer.
- El provider se carga sólo si está configurado.
- El fallback es explícito.
- Required no puede pasar silenciosamente sin cobertura completa.
- DEP001/DEP002 pueden consumir edges semánticos mediante fake provider.
- La observación está fingerprinted y digest-bound.
- Los proyectos existentes no necesitan cambiar.
- No existe dependencia runtime de Roslynk/.NET/MCP.
- Todos los tests, docs, schemas y reglas están sincronizados.

---

# CHANGESET C — Bridge externo `aak-dotnet-roslynk`

## 28. Condición previa crítica

No construyas el bridge de validación sobre una secuencia de llamadas `find_references` por símbolo ni parseando los outlines compactos actuales como si fueran una API de exportación estable.

Las herramientas actuales de Roslynk son excelentes para el agente, pero una validación exhaustiva necesita una operación masiva con:

- schema versionado;
- cobertura declarada;
- ausencia de truncación oculta;
- target project y target namespace resueltos;
- inputs/fingerprints;
- target frameworks/configuraciones observadas;
- output determinista.

Antes del bridge real debe existir una de estas dos opciones:

### Opción preferida

Añadir upstream a Roslynk una herramienta read-only equivalente a:

```text
export_semantic_dependencies
```

### Opción alternativa

Crear un sidecar .NET separado que use Roslyn directamente y produzca el contrato AAK. En ese caso:

- Roslynk sigue siendo la herramienta interactiva del agente;
- el sidecar es el proveedor determinista de CI;
- no se debe afirmar que el snapshot procede de Roslynk;
- el provider se llamaría, por ejemplo, `dotnet_roslyn`, no `roslynk`.

No copies implementación interna de Roslynk salvo decisión explícita, atribución de licencia MIT y aceptación consciente del coste de mantenimiento. Se prefiere integración upstream o dependencia publicada estable.

## 29. API requerida en Roslynk

Proponer una operación read-only:

```text
export_semantic_dependencies(
    solutionId,
    scopePaths?,
    includeGenerated=false,
    includeExternal=false
)
```

Debe devolver JSON estructurado o contenido MCP estructurado, no sólo outline humano.

### 29.1. Resultado mínimo

```json
{
  "schemaVersion": 1,
  "provider": {
    "name": "roslynk",
    "version": "1.1.x"
  },
  "subject": {
    "solutionPath": "Product.slnx"
  },
  "coverage": {
    "status": "complete",
    "truncated": false,
    "projects": [],
    "configurations": [],
    "sourceFiles": [],
    "exclusions": []
  },
  "inputs": [
    {"path": "Product.slnx", "sha256": "..."}
  ],
  "dependencies": [
    {
      "sourcePath": "...",
      "sourceNamespace": "...",
      "sourceSymbol": "...",
      "targetNamespace": "...",
      "targetSymbol": "...",
      "targetProjectPath": "...",
      "locations": [],
      "configurations": []
    }
  ]
}
```

### 29.2. Semántica de cobertura

- Un edge compartido por varios TFMs se deduplica y conserva su lista de configuraciones.
- Ramas `#if` observadas se reflejan en configuraciones/proyecciones.
- Un proyecto que no pudo cargarse impide `complete`.
- Diagnósticos de carga deben distinguirse de diagnósticos normales de compilación.
- `includeExternal=false` puede omitir targets externos, pero nunca repository-local.
- Código generado y Razor deben quedar incluidos o excluidos de forma explícita.
- No debe existir un `maxResults` implícito para la exportación de CI. Si existe límite, alcanzar el límite marca `truncated=true`.

## 30. Package externo

Crear una distribución separada:

```toml
[project]
name = "aak-dotnet-roslynk"
version = "0.1.0"
dependencies = ["agentic-architecture-kit==<exact-compatible-version>"]

[project.entry-points."agentic_architecture_kit.semantic_observers"]
roslynk = "aak_dotnet_roslynk:observe"
```

Responsabilidades:

1. Leer config provider-specific.
2. Resolver exactamente una solución.
3. Conectarse por stdio self-launching o loopback HTTP.
4. Verificar server name/version/capability.
5. Abrir la solución y esperar estado listo.
6. Solicitar export completa.
7. Validar schema upstream.
8. Convertir al modelo AAK.
9. Normalizar paths y orden.
10. Entregar errores estructurados.
11. No escribir en el repositorio.
12. No decidir PASS/FAIL arquitectónico.

## 31. Configuración del consumidor

El consumer pinnea la extensión:

```json
{
  "extensions": [
    {
      "distribution": "aak-dotnet-roslynk",
      "version": "0.1.0"
    }
  ]
}
```

Y selecciona el provider en policy:

```json
{
  "observation": {
    "semantic": {
      "provider": "roslynk",
      "mode": "required",
      "solution": "Product.slnx",
      "capabilities": ["source-dependencies"]
    }
  }
}
```

No guardar en policy:

- command lines arbitrarias;
- tokens;
- paths absolutos;
- puertos privados específicos del usuario;
- secretos.

La selección de transport puede ser configuración local segura o una opción limitada del provider, nunca shell libre procedente del repositorio.

## 32. Tests del bridge

Además de tests unitarios, crear fixtures reales para:

- unused using;
- fully-qualified dependency;
- alias using;
- global using;
- partial class;
- same-named symbols;
- extension method;
- multiple target frameworks;
- conditional compilation;
- Razor/code-behind;
- generated code incluido/excluido;
- project load failure;
- indexing timeout;
- stale file durante observación;
- truncation;
- daemon ya ejecutándose;
- stdio self-launching;
- cancelación y cleanup.

El package externo puede tener una matriz CI con la versión exacta de .NET y Roslynk que declara soportar.

## 33. Definition of Done del Changeset C

- No se parsean respuestas humanas para inferir un grafo exhaustivo.
- El provider reporta cobertura real.
- AAK valida sus inputs y fingerprints.
- Las pruebas negativas demuestran que el analyzer miró el código.
- La distribución y versión están pinneadas.
- El bridge no escribe código ni policy.
- La ausencia de Roslynk produce estado estructurado, no “no dependencies”.

---

# CHANGESET D — Activación inicial y release

## 34. Ejemplos de consumo

Añadir un ejemplo mínimo, sin crear estructura especulativa, que pruebe:

```text
examples/dotnet-semantic-valid
```

Y una mutación o fixture inválido para:

```text
module -> host via fully-qualified symbol
```

El ejemplo debe ser pequeño, compilable y demostrar algo que el adapter sintáctico por sí solo no puede demostrar correctamente.

No dupliques un producto artificial grande sólo para enseñar el feature.

## 35. CI

### Núcleo AAK

- sigue sin Roslynk;
- usa fake provider;
- prueba schema, merge, engine y reglas.

### Job opcional de integración

- instala .NET requerido;
- instala/pinnea Roslynk y `aak-dotnet-roslynk`;
- ejecuta fixtures semánticos;
- conserva snapshot y manifest como artifacts;
- no bloquea plataformas no soportadas salvo que el release declare esa garantía.

### Consumer CI

Cuando mode sea `required`, la pipeline debe instalar la extensión y Roslynk antes de:

```bash
aak validate --base-ref "$BASE" --fail-on-review
```

## 36. Capability matrix

Sólo después de pruebas reales:

```text
Agent-side semantic discovery guidance — Implemented
Provider-neutral semantic observation contract — Implemented
.NET semantic source-dependency observation through Roslynk — Initial
Compiler-grade symbol graph — Roadmap o Initial, según lo realmente expuesto por AAK
```

No mover “compiler-grade symbol graph” a Implemented si AAK sólo consume dependency edges y el agente usa Roslynk fuera del validator.

## 37. Versionado

La introducción de nuevos campos opcionales puede ser backward compatible, pero la nueva capability y regla justifican una release minor preview, por ejemplo `0.5.0`, según la política real del repositorio.

Actualizar de forma consistente:

- `pyproject.toml`;
- `__version__`;
- templates con versión;
- URLs de schema en artefactos self-hosted;
- README y traducción;
- release docs;
- toolchain del propio AAK;
- ejemplos;
- tests de version pinning.

No hagas el bump al comienzo. Hazlo cuando el changeset esté completo y validado.

---

## 38. Mapa de archivos esperado en AAK

La lista es orientativa; Codex debe respetar el ownership real descubierto.

```text
architecture/decisions/ADR-<next>-semantic-code-intelligence.md

src/agentic_architecture_kit/
  model.py
  engine.py
  context.py
  context_cli.py
  guide_cli.py
  toolchain.py                         # sólo si hace falta para el contrato
  semantic_observers/
    __init__.py
    contracts.py
    fingerprint.py
    merge.py
  adapters/
    dotnet.py
  data/
    rules.json
    schemas/
      architecture-policy.schema.json
      semantic-observation.schema.json
    norms/
      portable-rules.md
      <classification files if applicable>
    guides/
      implement-change-prompt.md
      semantic-code-intelligence.md
    templates/project/
      AGENTS.md

src/agentic_architecture_kit/data/templates/project/...
README.md
AGENTS.md                                # sólo si cambia el router del propio kit
MANIFESTO.md                             # sólo si cambia una afirmación estable del manifesto
docs/capabilities.md
docs/semantic-code-intelligence.md
docs/es/capabilities.md
docs/es/semantic-code-intelligence.md
docs/es/README.md                        # si enlaza guías

tests/
  test_semantic_observation.py
  test_semantic_merge.py
  test_semantic_policy.py
  test_validator.py                      # sólo integraciones necesarias

examples/
  dotnet-semantic-valid/                 # Changeset D
```

No crees todos estos archivos por obligación si una función encaja claramente en un owner existente. Tampoco concentres toda la implementación nueva en `engine.py` o en el archivo de tests monolítico.

---

## 39. Orden técnico de implementación dentro del Changeset B

Seguir este orden para mantener cada paso verificable:

1. Escribir ADR y contract tests del schema.
2. Añadir config opcional sin cambiar comportamiento.
3. Añadir modelos frozen y serialización canónica.
4. Implementar validación de paths e input manifest.
5. Implementar fingerprint.
6. Implementar loader con fake provider.
7. Implementar merge puro y sus tests.
8. Marcar observación base C# como sintáctica.
9. Integrar una sola carga/merge en el validation pipeline.
10. Añadir `OBS001` y documentación normativa.
11. Conectar DEP001/DEP002 a merged observation.
12. Integrar context index/status.
13. Integrar task evidence/digests.
14. Implementar base comparison de enforcement.
15. Añadir fixtures end-to-end con fake provider.
16. Actualizar docs/capabilities/traducciones.
17. Ejecutar self-validation y corregir findings por causa.
18. Hacer el bump de versión al final.

Después de cada bloque, ejecutar tests focalizados y luego suite completa.

---

## 40. Comandos de validación

### Suite principal

```bash
python3 -m pip install --no-deps -e .
python3 -m compileall -q src tests tools
python3 -m unittest discover -s tests -v
```

### Recursos y CLI

```bash
aak --help
aak guide
aak guide semantic-code-intelligence
aak guide implement-change
aak context --help
aak context status
aak context index
```

### Arquitectura del propio kit

```bash
aak validate --fail-on-review
aak validate --base-ref <TARGET_BASE> --fail-on-review
```

### Ejemplos

```bash
aak validate --root examples/dotnet-valid --fail-on-review
aak validate --root examples/dotnet-invalid --fail-on-review
# Cuando exista:
aak validate --root examples/dotnet-semantic-valid --fail-on-review
```

### Packaging

Construir la distribución con el mecanismo utilizado por el repositorio y verificar que contiene:

```text
data/guides/semantic-code-intelligence.md
data/schemas/semantic-observation.schema.json
data/norms/rule references actualizadas
data/templates/project/AGENTS.md
```

No declarar completion sólo porque los unit tests pasan; validar también package resources y self-hosting.

---

## 41. Criterios de aceptación globales

La iniciativa está completa cuando se cumplen todos los siguientes criterios aplicables al changeset entregado.

### Experiencia del agente

- Existe una guía versionada accesible mediante `aak guide`.
- El agente sabe usar AAK y Roslynk sin confundir autoridad con observación.
- El workflow exige provider/evidence level.
- Diagnostics no sustituye build/tests.

### Compatibilidad

- Proyectos sin semantic config conservan comportamiento.
- Python y adapters externos existentes no requieren Roslynk.
- El package principal conserva Python 3.9+ y cero nuevas dependencias runtime de terceros, salvo decisión explícita distinta.

### Evidencia

- Provider, versión, coverage, inputs y fingerprint son trazables.
- Dirty worktrees quedan ligados a contenido real.
- No hay paths absolutos persistidos.
- Snapshots stale no se aceptan.

### Merge

- Complete semantic coverage puede eliminar un unused-using false positive.
- Fully-qualified actual reference aparece aunque no haya using.
- Partial/unavailable nunca significa “no dependencies”.

### Enforcement

- Required incompleto produce review/failure visible.
- `--fail-on-review` bloquea.
- Reducir required a advisory queda protegido por base comparison.
- Observación nunca escribe permisos.

### Calidad

- Pruebas positivas y negativas.
- Fake provider en core CI.
- Integración real sólo en package/job separado.
- Documentación inglesa y española sincronizada.
- Capability matrix no exagera garantías.

---

## 42. Atajos prohibidos

Codex no debe:

1. Añadir texto a `AGENTS.md` y declarar la integración terminada.
2. Cambiar todos los `using` a “semantic” sin resolver símbolos.
3. Considerar un resultado vacío como evidencia de ausencia cuando hubo error.
4. Parsear texto destinado al LLM como contrato de CI sin schema/version.
5. Hacer una llamada MCP por símbolo y llamarla exportación exhaustiva.
6. Permitir que el provider modifique policy o cree waivers.
7. Ejecutar command strings arbitrarias leídas del repositorio.
8. Ocultar cobertura parcial mediante fallback.
9. Hacer Roslynk obligatorio para el propio AAK, Python o todos los consumers.
10. Sustituir build/tests por `get_diagnostics`.
11. Persistir el solution path absoluto del equipo.
12. Añadir un nuevo module AAK sólo porque existe una tecnología nueva; primero comprobar el owner cohesivo existente.
13. Marcar capacidades como Implemented sin comando/contrato, tests y ejemplo cuando aplique.
14. Debilitar una regla para conseguir PASS.
15. Crear una solución, proyecto o directorio especulativo para satisfacer el tooling.
16. Autorizar su propia desviación arquitectónica.

---

## 43. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Acoplamiento a formato textual Roslynk | Exigir export schema-versioned o sidecar propio |
| Daemon stale | Input manifest + fingerprint + revisión de status |
| Resultados truncados | `truncated` invalida complete coverage |
| Coste de análisis grande | Una instantánea por workspace fingerprint; cache segura fuera del repo |
| Multi-TFM/#if incompleto | Configurations y coverage explícitas |
| Roslynk no disponible en CI | Provider opcional; required sólo por decisión del consumer |
| Falsos positivos de `using` | Sustitución sólo bajo complete semantic coverage |
| Falsos negativos por archivos no cubiertos | Conservar fallback y producir review cuando required |
| AAK se convierte en IDE | No envolver herramientas generales; limitar core a evidencia arquitectónica |
| Cambio de provider reduce garantía | Toolchain pin + policy/base comparison |
| Exposición de paths/secrets | Paths relativos, redacción y loopback/read-only |
| Core tests frágiles por .NET | Fake provider; real integration en package separado |

---

## 44. Preguntas que Codex no debe trasladar al usuario

Codex debe resolver del repositorio y del plan:

- nombres de archivos internos;
- ubicación de tests;
- implementación del loader;
- serialización canónica;
- estructura de error codes;
- siguiente número ADR;
- actualización de package resources;
- cómo mockear entry points;
- orden de sorting/dedup;
- cómo actualizar traducciones técnicas.

Sólo existe una posible decisión material que puede requerir autoridad humana:

> ¿Debe un consumer concreto exigir observación semántica (`required`) o usarla sólo como optimización advisory?

Para el propio kit y sus templates, el default debe ser **no configurado/advisory**, nunca required universal.

---

## 45. Resultado esperado de Codex

Al finalizar cada changeset, reportar:

```text
Product outcome delivered:
Primary change classification:
Architectural owner:
Files changed:
Public contracts added or changed:
Compatibility impact:
Semantic provider behavior:
Fallback behavior:
Rules/findings added or changed:
Tests executed and exact results:
Packaging verification:
AAK self-validation result:
Base-comparison result:
Deferred work and why:
Upstream Roslynk dependency/blocker, if any:
```

No ocultar trabajo diferido. En particular, si Roslynk todavía no ofrece una exportación semántica masiva y estable, completar Changesets A y B con fake provider, documentar el contrato requerido y declarar Changeset C bloqueado; no simular que el bridge exhaustivo existe.

---

## 46. Resumen ejecutivo para la implementación

La implementación correcta no consiste en “añadir Roslynk a AAK” como una dependencia directa.

Consiste en:

1. enseñar al agente a combinar **autoridad arquitectónica AAK** con **inteligencia del compilador Roslynk**;
2. definir en AAK un contrato pequeño para evidencia semántica que sea versionado, determinista y seguro;
3. mantener Roslynk y su bridge fuera del núcleo;
4. sustituir candidates sintácticos únicamente cuando haya cobertura semántica completa;
5. fallar de forma visible cuando el proyecto exige una garantía que no puede demostrarse;
6. conservar build, tests, Git y governance como pruebas finales independientes.

El objetivo final es que AAK pueda responder:

```text
“This dependency is architecturally forbidden”
```

usando evidencia que Roslyn pueda expresar como:

```text
“This exact symbol in this exact file and configuration references that exact
repository-local symbol/project at this location.”
```

sin que ninguno de los dos componentes invada la responsabilidad del otro.
