# Manifiesto de arquitectura de repositorio para agentes de programación

## Protocolo de inicialización, evolución y conformidad — versión 2 revisada

[English — canonical](../../MANIFESTO.md) · [Política lingüística](language-policy.md)

> **Estado:** normativo.
>
> **Implementación de referencia:** los requisitos normativos y la capacidad
> entregada se distinguen deliberadamente. Consulta
> [`capabilities.md`](capabilities.md) para la implementación probada, las
> garantías iniciales limitadas y la hoja de ruta.
>
> **Ámbito:** este manifiesto define reglas portables para crear y hacer
> evolucionar repositorios mediante agentes de programación. Cada proyecto debe
> especializarlas mediante una política propia. Las excepciones requieren una
> licencia explícita y nunca modifican silenciosamente las reglas generales.
>
> **Principio rector:** el agente razona y propone; el repositorio declara,
> localiza, restringe, valida y conserva evidencia.

---

# 1. Propósito

Este manifiesto no prescribe un árbol exhaustivo que deba copiarse. Define un
protocolo para producir la arquitectura mínima correcta con el conocimiento
disponible y para hacerla crecer cuando aparezcan necesidades verificables.

## 1.1 Objetivo principal: autonomía gobernada

> **Un agente debe poder crear, modificar y hacer evolucionar el proyecto de
> forma autónoma dentro de los límites decididos por el equipo. El repositorio
> debe proporcionarle suficiente contexto, políticas y validaciones para
> determinar qué puede hacer, dónde debe hacerlo y cómo demostrar que el
> resultado es conforme, sin solicitar intervención humana salvo cuando la
> petición requiera una decisión de producto, riesgo, ownership o autoridad que
> todavía no esté definida. Además, el repositorio debe organizar y proporcionar
> de forma eficiente, progresiva y trazable el contexto mínimo suficiente para
> cada tarea, de modo que el agente pueda localizar rápidamente el dominio,
> ownership, contratos, decisiones, dependencias, código y tests relevantes sin
> cargar información indiscriminada ni depender de memoria conversacional.**

La autonomía es la conducta predeterminada. El agente `MUST` continuar cuando la
petición se encuentre dentro de la autoridad y los límites ya declarados. No
solicita confirmación para decisiones de implementación reversibles que pueda
resolver mediante contratos, invariantes, ADR, política y evidencia existentes.

El agente escala únicamente cuando continuar exigiría asumir una decisión
material que el equipo no ha delegado, como cambiar el producto, aceptar un
riesgo, trasladar ownership, debilitar una regla o realizar una operación fuera
de la autoridad concedida. La ausencia de una preferencia secundaria no basta
por sí sola para interrumpir el trabajo.

El acceso al contexto es una responsabilidad arquitectónica. El repositorio
`MUST` ofrecer un bootstrap pequeño y determinista, y `MUST` permitir que el
agente amplíe el contexto siguiendo ownership, contratos, dependencias,
consumidores, datos, tests y evidencia concreta. El agente `MUST NOT` sustituir
esta navegación progresiva por una carga indiscriminada del repositorio.

El contexto recuperado `SHOULD` identificar su procedencia y distinguir hechos
declarados, hechos observados, inferencias y preguntas abiertas. La memoria de
una conversación `MUST NOT` ser necesaria para reconstruir el estado actual de
la arquitectura o continuar el desarrollo.

El resultado buscado es un repositorio donde un agente pueda responder:

```text
¿Qué capacidad funcional posee esta petición?
¿Dónde comienza el comportamiento relacionado?
¿Qué reglas e invariantes lo gobiernan?
¿Qué código, datos y contratos afecta?
¿Qué dependencias están permitidas?
¿Qué tests y validaciones son obligatorios?
¿Qué evidencia demuestra que el cambio está completo?
¿Qué desviaciones están autorizadas y por qué?
```

Nombre descriptivo:

> **Arquitectura modular por capacidades y vertical slices, con evolución
> incremental, navegación determinista y entrega basada en evidencia.**

El manifiesto pertenece al ámbito de *Agentic Software Engineering*. No define
una arquitectura de sistemas multiagente ni introduce un nuevo significado para
el acrónimo histórico AOSE.

---

# 2. Lenguaje normativo

Los términos `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT` y `MAY` expresan el nivel
de obligatoriedad:

- `MUST` / `MUST NOT`: regla general obligatoria;
- `SHOULD` / `SHOULD NOT`: recomendación que solo se omite con una razón
  explícita;
- `MAY`: posibilidad permitida, nunca estructura obligatoria.

Una política de proyecto puede concretar una regla general. No puede debilitarla
silenciosamente. Para desviarse debe registrar una licencia acotada.

---

# 3. Principios universales

## 3.1 La arquitectura se basa en conocimiento actual

> **Architectural decisions MUST be based on current requirements and observable
> project evidence. An agent MUST NOT introduce modules, projects, abstractions,
> shared components, or directory levels solely for anticipated future use.**

Una necesidad futura incierta se registra como riesgo, supuesto o pregunta. No
se convierte en estructura hasta que exista un consumidor o límite real.

```text
Necesidad posible
→ riesgo o pregunta documentada
→ no se materializa todavía
```

## 3.2 Economía estructural

> **Every module, project, directory, abstraction, and shared component MUST be
> justified by current code or by an enforced boundary.**

Por tanto:

- no se crean carpetas vacías para completar una plantilla;
- no se crea una carpeta por cada clase;
- varias clases pequeñas y cohesivas pueden compartir archivo cuando se
  localizan, cambian y revisan juntas;
- una clase obtiene archivo propio cuando tiene responsabilidad, navegación o
  evolución independiente;
- un proyecto o assembly existe solo cuando impone un límite verificable de
  dependencia, despliegue, ownership, lenguaje o runtime;
- `Shared`, `Common`, `BuildingBlocks` y abstracciones comunes aparecen solo con
  consumidores actuales y ownership explícito;
- un árbol más grande no representa una arquitectura más madura.

## 3.3 Organización por capacidad funcional

Los módulos representan capacidades del producto:

```text
Modules/
├── Competitions/
├── Classification/
├── Payments/
└── Identity/
```

Categorías técnicas no son módulos funcionales:

```text
Git/
Providers/
Repositories/
Validation/
Services/
```

Esas responsabilidades permanecen dentro de la infraestructura del módulo que
las utiliza, salvo que sean una plataforma realmente independiente con contrato,
ownership y ciclo de vida propios.

## 3.4 Vertical slice y cohesión de feature

Todo comportamiento nuevo comienza en el módulo propietario y en el área
funcional más pequeña que posea su vocabulario, estado y ciclo de vida:

```text
src/Modules/{Module}/Features/{FeatureArea}/
```

> **A command, handler, endpoint, or use case MUST NOT automatically create a new
> root feature directory.**

Varias operaciones permanecen en una feature cuando:

- actúan sobre el mismo concepto o agregado;
- comparten estado, almacenamiento o ciclo de vida;
- están gobernadas por los mismos invariantes;
- sus cambios exigen revisar sustancialmente el mismo contexto;
- separarlas aumenta la navegación sin establecer un límite real.

Una feature raíz nueva requiere independencia observable, como vocabulario,
ownership, invariantes, riesgo, dependencias o evolución propios.

Ejemplo válido:

```text
Modules/Planning/Features/
├── Plan/
│   ├── PlanOrchestrator.cs
│   ├── Prompts/
│   ├── Schemas/
│   └── Validation/
├── Environment/
│   └── DoctorService.cs
└── Run/
    ├── ShowRunService.cs
    └── PruneRunService.cs
```

`ShowRun` y `PruneRun` permanecen juntas porque comparten el concepto y ciclo de
vida de `Run`.

## 3.5 Clean Architecture es local, no una taxonomía global

Cuando aporta límites útiles, un módulo puede contener:

```text
Module
├── Domain/
├── Contracts/
├── Features/
└── Infrastructure/
```

Estas carpetas son posibilidades, no placeholders. Un módulo sin reglas de
dominio propias no crea `Domain/`. Un módulo sin adaptadores técnicos no crea
`Infrastructure/`.

## 3.6 Declaración y observación son distintas

La arquitectura declarada expresa intención y ownership. La arquitectura
observada se deriva del código, configuración y artefactos de build.

```text
Declarado                         Observado
-----------------------------    --------------------------------
propósito del módulo             proyectos y assemblies
aliases funcionales              namespaces y símbolos
ownership                        dependencias
riesgo                           endpoints y handlers
invariantes y ADR                acceso a datos y tests
```

> **Architectural conformance MUST compare declared architecture with observed
> architecture. Validating policy or contract syntax alone is not architectural
> conformance.**

## 3.7 Sin evidencia no hay completitud

La afirmación de un agente nunca satisface por sí sola un quality gate. La
completitud se deriva de build, tests, análisis estático, validaciones de riesgo,
evidencia ligada a la revisión y aprobaciones necesarias.

---

# 4. Capas de conformidad

La conformidad arquitectónica separa tres capas.

## 4.1 Reglas generales del manifiesto

Son portables entre proyectos. Deben tener identificadores estables:

```text
POL001  Project architecture policy is valid
ARC001  Declared and observed architecture agree
MOD001  Every module has a semantic contract
MOD002  Module id matches its module root
MOD003  Technical categories are not product modules
FEAT001 Application behavior belongs to an owning feature area
HOST001 Hosts do not own application behavior
DEP001  Modules do not depend on hosts
DEP002  Cross-module access uses public contracts
DEP003  Observed project dependencies are authorized
OWN001  Authoritative data has one owner
STR001  Speculative structure is prohibited
DOC001  Invariant and ADR references resolve
WVR001  Waivers are explicit and valid
```

Las reglas generales pertenecen al catálogo ejecutable suministrado con el
manifiesto, no a la implementación particular de un repositorio. Cada entrada
declara su evaluador, entradas necesarias y si puede resolverse automáticamente.

## 4.2 Política específica del proyecto

Cada proyecto declara cómo materializa el manifiesto. Puede describir módulos,
hosts, assemblies, límites, dependencias y reglas propias.

La política cumple `architecture-policy.schema.json`. Ejemplo abreviado:

```json
{
  "$schema": "../../contracts/schemas/architecture-policy.schema.json",
  "version": 1,
  "project": "acme",
  "adapter": "dotnet",
  "roots": {
    "modules": "src/Modules",
    "hosts": "src/Hosts"
  },
  "projectSearchRoots": ["src"],
  "structureSearchRoots": ["src"],
  "moduleContract": {
    "fileName": "module.contract.yml",
    "schema": ".agentic/contracts/schemas/module-contract.schema.json",
    "forbiddenStructuralFields": ["paths", "handlers", "classes", "tests"]
  },
  "technicalModuleNames": ["Git", "Providers", "Validation"],
  "forbiddenDirectoryNames": ["Services", "Helpers", "Common"],
  "modules": [
    {
      "id": "orders",
      "root": "src/Modules/Orders",
      "featureRoot": "src/Modules/Orders/Features",
      "featureAreas": ["OrderLifecycle"]
    }
  ],
  "hosts": [
    {
      "id": "api",
      "root": "src/Hosts/Api",
      "allowedSourcePatterns": ["Program.cs", "Endpoints/*.cs"]
    }
  ],
  "projects": [
    {
      "path": "src/Modules/Orders/Orders.csproj",
      "name": "Acme.Orders",
      "owner": { "kind": "module", "id": "orders" },
      "role": "application"
    },
    {
      "path": "src/Hosts/Api/Api.csproj",
      "name": "Acme.Api",
      "owner": { "kind": "host", "id": "api" },
      "role": "host"
    }
  ],
  "allowedProjectDependencies": [
    {
      "from": "src/Hosts/Api/Api.csproj",
      "to": "src/Modules/Orders/Orders.csproj"
    }
  ]
}
```

La política del proyecto puede contener información estructural porque su
propósito es validar la materialización física. No debe duplicar hechos que el
analizador pueda descubrir de forma fiable, salvo cuando expresen un límite
deseado que deba compararse con lo observado.

## 4.3 Licencias arquitectónicas

Una licencia autoriza una desviación concreta sin modificar la regla general.

```json
{
  "version": 1,
  "waivers": [
    {
      "id": "ACME-ARCH-001",
      "rule": "DEP002",
      "scope": "src/Modules/Reporting/Features/LegacyImport",
      "decision": "Temporarily allow direct access to Billing infrastructure.",
      "reason": "The import has not yet migrated to Billing contracts.",
      "risk": "Reporting remains coupled to an internal implementation.",
      "authorizedBy": [
        "architecture/decisions/ADR-021-legacy-import-migration.md"
      ],
      "expiresOn": "2026-12-31",
      "reviewWhen": [
        "Billing publishes the required import contract",
        "the legacy import is modified"
      ]
    }
  ]
}
```

Cada licencia `MUST` incluir:

- regla afectada;
- scope exacto;
- decisión y motivo;
- ADR o autoridad que la aprueba;
- riesgo o compensación relevante;
- condición de revisión o caducidad cuando sea aplicable.

Una licencia no convierte el resultado en un `PASS` silencioso. Los estados de
conformidad son:

```text
PASS
FAIL
WAIVED
NOT_APPLICABLE
REVIEW_REQUIRED
```

## 4.4 Regla de separación

> **Conformance MUST separate portable manifesto rules, project-specific policy,
> and authorized waivers. A project waiver MUST NOT silently weaken or redefine
> a general rule.**

---

# 5. Protocolo de inicialización de un proyecto

Este protocolo se aplica cuando un agente recibe un repositorio vacío o un
producto que todavía no tiene arquitectura establecida.

## 5.1 Descubrimiento inicial

El agente comienza con la información disponible:

- objetivo y alcance actual del producto;
- actores y operaciones conocidas;
- datos y ownership conocidos;
- interfaces externas requeridas;
- restricciones de lenguaje, runtime y despliegue;
- riesgos e invariantes conocidos;
- comandos de build y test disponibles.

La ausencia de información se registra como pregunta o supuesto. No se rellena
con arquitectura inventada.

## 5.2 Identificación de capacidades

El agente agrupa comportamiento por vocabulario, ownership, reglas y ciclo de
vida. Solo crea varios módulos cuando existen límites funcionales reales.

Preguntas de decisión:

```text
¿Tiene vocabulario propio?
¿Posee datos o estado?
¿Tiene invariantes propios?
¿Puede evolucionar de forma independiente?
¿Necesita un contrato con otras capacidades?
```

Una respuesta negativa o desconocida favorece mantener el comportamiento en un
módulo existente o comenzar con un solo módulo.

## 5.3 Identificación de hosts

Un host representa una forma de ejecutar o exponer el producto, por ejemplo:

```text
Hosts/
├── Api/
├── Cli/
├── Worker/
└── Mcp/
```

Solo se crea un host que el producto necesite actualmente. El host adapta entrada
y salida, compone dependencias y delega. No posee comportamiento de aplicación.

## 5.4 Identificación de límites compilables

Un proyecto o assembly nuevo necesita al menos una razón actual:

- impedir dependencias prohibidas;
- separar despliegues;
- separar runtime o lenguaje;
- aislar ownership;
- publicar un contrato independiente.

“Podría crecer” no es una razón suficiente.

## 5.5 Entregables mínimos

El agente crea únicamente los artefactos aplicables:

```text
repository/
├── AGENTS.md
├── architecture/
│   ├── system-overview.md
│   ├── boundaries.md
│   └── decisions/
├── domain/
│   ├── glossary.md
│   ├── global-invariants.md
│   └── contexts/
├── src/
│   ├── Modules/
│   │   └── {CurrentModule}/
│   │       ├── AGENTS.md
│   │       ├── module.contract.yml
│   │       └── Features/
│   └── Hosts/                         # solo si existe un host
├── tests/
│   └── Architecture/
└── .agentic/
    ├── contracts/
    └── policies/
        └── architecture/
```

Las carpetas sin contenido o responsabilidad actual se omiten.

## 5.6 Arquitectura inicial ejecutable

La inicialización no termina al dibujar el árbol. El agente `MUST` crear
validaciones para los límites que acaba de declarar.

Como mínimo:

- descubrir módulos y hosts;
- validar contratos e identificadores;
- comprobar dependencias permitidas;
- impedir dependencias de módulos hacia hosts;
- comprobar enlaces a invariantes y ADR;
- comparar los límites declarados con proyectos y referencias observados;
- producir resultados `PASS`, `FAIL`, `WAIVED`, `NOT_APPLICABLE` o
  `REVIEW_REQUIRED`.

---

# 6. Protocolo de evolución

Cada plan de implementación o petición de desarrollo ejecuta este protocolo.

## 6.1 Localizar antes de crear

El agente decide en este orden:

1. ¿Qué módulo posee la petición?
2. ¿Qué feature posee su concepto y ciclo de vida?
3. ¿Es una operación dentro de esa feature?
4. ¿La complejidad actual justifica una subcarpeta?
5. ¿Existe lógica compartida real que deba promocionarse?
6. ¿Ha aparecido una capacidad que justifique un módulo nuevo?
7. ¿Hace falta un assembly para imponer un límite verificable?

La respuesta predeterminada es extender el límite cohesivo existente, no crear
estructura nueva.

## 6.2 Regla de ubicación

El comportamiento específico permanece en `Features/{FeatureArea}` cuando:

- orquesta una operación de esa capacidad;
- transforma entrada y salida;
- contiene validaciones específicas;
- coordina puertos para ese comportamiento;
- no representa una regla autónoma de dominio.

Se promociona a `Domain/` cuando representa una regla con significado propio,
independiente de infraestructura y compartida por comportamiento actual.

Se promociona a `Contracts/` cuando otros módulos o hosts necesitan consumirla
como API pública.

Se coloca en `Infrastructure/` cuando implementa acceso a filesystem, red,
persistencia, procesos, mensajería, SDK o servicios externos.

## 6.3 Crecimiento justificado

### Nueva subcarpeta de operación

Se crea cuando la operación tiene suficiente contenido, navegación o evolución
independiente. No se crea por la mera existencia de un comando.

### Nueva feature raíz

Se crea cuando existe vocabulario, estado, invariantes, riesgo o ciclo de vida
propios dentro del módulo.

### Nuevo módulo

Se crea cuando aparece una capacidad funcional con ownership y contratos
independientes. Nunca para representar una categoría técnica.

### Nuevo assembly

Se crea cuando impone un límite real de dependencia, despliegue, runtime,
lenguaje, distribución u ownership.

### Componente compartido

Se crea cuando existen al menos dos consumidores actuales, responsabilidad
cohesiva y ownership explícito. La duplicación pequeña puede ser preferible a
una abstracción prematura.

## 6.4 Cambio arquitectónico atómico

> **A change that modifies an architectural boundary is incomplete until the
> declared architecture, observed structure, enforcement rules, and
> documentation agree.**

Un cambio de límite actualiza conjuntamente lo aplicable:

- código y proyectos;
- contrato semántico del módulo;
- `AGENTS.md` local;
- documentos de dominio;
- ADR;
- política específica del proyecto;
- tests arquitectónicos;
- índice estructural;
- licencias;
- evidencia del cambio.

## 6.5 Autoridad de planes y peticiones

Un plan de implementación es una entrada, no autoridad arquitectónica superior.

```text
Petición o plan
        ↓
Reglas generales del manifiesto
        ↓
Política y licencias del proyecto
        ↓
Contratos, invariantes y ADR
        ↓
Implementación
```

Si un plan contradice una regla:

1. el agente intenta una solución compatible;
2. si la desviación es necesaria, propone un ADR y una licencia;
3. si altera significativamente ownership, riesgo o producto, solicita decisión;
4. nunca introduce la excepción silenciosamente.

---

# 7. Gramática estructural permitida

Esta sección enumera ubicaciones posibles. No es un árbol obligatorio.

```text
repository/
├── AGENTS.md
├── architecture/                    # decisiones y límites mantenidos
├── domain/                          # vocabulario e invariantes
├── src/
│   ├── Modules/                     # capacidades funcionales
│   ├── Hosts/                       # formas actuales de ejecución
│   └── BuildingBlocks/              # excepcional, con consumidores reales
├── web/                             # si existe frontend independiente
├── tests/
├── docs/
├── tools/
└── .agentic/
```

Un módulo puede materializar solo las áreas necesarias:

```text
src/Modules/{Module}/
├── AGENTS.md                         # obligatorio
├── module.contract.yml               # obligatorio
├── Domain/                           # opcional
├── Contracts/                        # opcional
├── Features/                         # cuando existe comportamiento
└── Infrastructure/                   # cuando existen adaptadores técnicos
```

Carpetas genéricas como `Managers`, `Helpers`, `Utils`, `Common` o
`Application/Services` están prohibidas por defecto porque ocultan ownership.
Solo una licencia con responsabilidad y scope acotados puede autorizarlas.

---

# 8. Contrato semántico del módulo

Cada módulo mantiene:

```text
src/Modules/{Module}/module.contract.yml
```

Ejemplo:

```yaml
id: classification
name: Classification

purpose: >
  Calculates standings, rankings, and tie-break rules.

intent:
  aliases:
    - classification
    - standings
    - ranking
    - league table

ownership:
  domain: competition-classification
  authoritative_data:
    - ClassificationSnapshots

risk:
  default: high
  reasons:
    - Business-critical calculation

invariants:
  - domain/contexts/classification.md#team-inclusion
  - domain/contexts/classification.md#disqualified-teams

architecture_decisions:
  - architecture/decisions/ADR-014-classification-rules.md
```

El contrato contiene semántica que no puede derivarse de forma fiable:

- propósito;
- vocabulario e intención;
- ownership;
- riesgo;
- invariantes;
- ADR aplicables.

No contiene hechos estructurales derivables:

```yaml
paths:
entrypoints:
handlers:
classes:
tests:
entities_read:
entities_written:
routes:
```

La conformidad del contrato incluye forma y significado:

- cumple su schema;
- el `id` coincide con el módulo observado;
- referencias a invariantes y ADR existen;
- aliases no colisionan sin resolución;
- ownership declarado coincide con acceso observado;
- los datos autoritativos no reciben escrituras directas desde otro módulo.

---

# 9. Arquitectura observada e índice generado

La implementación de referencia 0.2 genera `repository`, `projects`, `modules`,
`dependencies`, `tests` y `documents`. Los demás índices de la lista siguiente
son puntos de extensión normativos y permanecen en la hoja de ruta hasta que un
adaptador pueda observarlos.

La estructura real se deriva del repositorio mediante adaptadores de lenguaje y
plataforma. Un índice puede residir en:

```text
.agentic/generated/index/
├── repository.json
├── projects.json
├── modules.json
├── symbols.json
├── references.json
├── dependencies.json
├── endpoints.json
├── handlers.json
├── entities.json
├── data-access.json
├── tests.json
└── documents.json
```

Solo se generan los índices relevantes para el proyecto.

Cada índice registra al menos:

```json
{
  "repositoryRevision": "73a9c45",
  "generatorVersion": "1.0.0",
  "generatedAt": "2026-07-27T10:00:00Z"
}
```

Un índice cuya revisión no coincide con el código está obsoleto y no puede
satisfacer validaciones.

Los adaptadores tecnológicos pueden extraer:

- proyectos, packages o assemblies;
- namespaces, símbolos y referencias;
- endpoints, handlers y registros de composición;
- entidades, tablas y migraciones;
- productores y consumidores de eventos;
- dependencias entre módulos;
- tests relacionados.

La herramienta general evalúa un modelo arquitectónico común. Los adaptadores
de .NET, Java, TypeScript, Python u otras plataformas construyen ese modelo sin
convertir reglas tecnológicas particulares en reglas universales.

---

# 10. Validación arquitectónica

## 10.1 Pipeline

```text
Código y configuración
        ↓
Modelo arquitectónico observado
        ↓
Reglas generales + política del proyecto
        ↓
Comparación con contratos y ADR
        ↓
Aplicación visible de licencias
        ↓
PASS / FAIL / WAIVED / REVIEWED / NOT_APPLICABLE / REVIEW_REQUIRED
```

## 10.2 Qué se valida automáticamente

Cuando la plataforma lo permita:

- módulos, hosts y contratos existen donde corresponde;
- identificadores y referencias son válidos;
- proyectos y dependencias respetan la política;
- módulos no dependen de hosts;
- hosts no contienen comportamiento de aplicación;
- infraestructura no se filtra hacia dominio o aplicación;
- acceso entre módulos atraviesa contratos públicos;
- namespaces o packages corresponden con su ownership;
- handlers y endpoints pertenecen a features;
- tests reflejan módulos y features;
- ownership de datos coincide con lecturas y escrituras observadas;
- licencias tienen scope, autoridad y vigencia válidos;
- el índice corresponde a la revisión actual.

## 10.3 Qué requiere revisión

Algunas decisiones son semánticas y no deben disfrazarse de comprobaciones
deterministas:

- si dos operaciones son realmente cohesivas;
- si una nueva capacidad merece un módulo;
- si una abstracción compensa su coste;
- si un nombre funcional describe correctamente el ownership;
- si una licencia sigue siendo razonable.

El analizador puede producir evidencia y heurísticas, pero el resultado será
`REVIEW_REQUIRED` cuando no pueda demostrar la regla.

Una autoridad delegada puede persistir una revisión semántica aceptada en
`reviews.json`. Solo se aplica a la regla, scope y huella exacta del hallazgo y
se informa como `REVIEWED`, nunca `PASS`. Si cambia la evidencia, la revisión
queda obsoleta y vuelve a aparecer `REVIEW_REQUIRED`.

## 10.4 Implementación de referencia suministrada

El manifiesto `MUST` distribuirse con un validador general versionado. Un agente
no reimplementa sus reglas para cada repositorio:

```text
tools/architecture/
├── rules.json                    # catálogo portable y estable
├── validate.py                   # CLI y ensamblaje del pipeline
├── validator/
│   ├── engine.py                 # evaluación y aplicación de licencias
│   ├── contracts.py              # contratos de entrada y salida
│   └── adapters/
│       ├── dotnet.py             # observación .NET
│       └── python.py             # observación Python
├── context.py                    # CLI de contexto progresivo
└── tests/                        # conformidad del propio validador
```

El proyecto suministra únicamente:

```text
.agentic/
├── contracts/schemas/
│   ├── architecture-policy.schema.json
│   ├── architecture-waivers.schema.json
│   ├── architecture-reviews.schema.json
│   └── architecture-result.schema.json
└── policies/architecture/
    ├── project-policy.json
    ├── waivers.json
    └── reviews.json
```

El agente puede añadir un adaptador tecnológico ausente o una comprobación
específica del proyecto. No puede redefinir silenciosamente el significado de
una regla general. Una regla no demostrable produce `REVIEW_REQUIRED`.

Comandos de referencia:

```bash
./tools/scripts/validate-architecture.sh
./tools/scripts/validate-architecture.sh --format json
./tools/scripts/validate-architecture.sh --base-ref origin/main
./tools/scripts/validate-architecture.sh --task-id TASK-123
./tools/scripts/validate-architecture.sh --fail-on-review
./tools/scripts/validate-architecture.sh --list-rules
```

`FAIL` devuelve código 1. Una entrada o configuración inválida devuelve código
2. `REVIEW_REQUIRED` queda visible y puede convertirse en bloqueo mediante
`--fail-on-review`.

## 10.5 Tests generales y específicos

La validación se divide físicamente:

```text
tools/architecture/tests/             # reglas y motor portables
tests/Architecture/                   # decisiones específicas del proyecto
```

El validador de referencia se prueba, como mínimo, contra:

- una arquitectura conforme;
- una dependencia no autorizada;
- una referencia documental rota;
- una licencia válida, visible y acotada;
- contratos o configuraciones inválidos.

Los tests específicos del proyecto amplían el catálogo cuando una regla depende
de semántica de dominio o tecnología que el modelo común no puede observar.

---

# 11. `AGENTS.md` como router

## 11.1 Router raíz

El `AGENTS.md` raíz es breve y contiene:

- propósito del repositorio;
- comandos autoritativos;
- reglas críticas;
- mapa de módulos y hosts;
- workflow inicial;
- operaciones prohibidas.

No contiene toda la arquitectura ni todo el dominio.

## 11.2 Router de módulo

Cada módulo mantiene orientación local:

```markdown
# Classification module

## Purpose

Calculates competition standings and tie-break rules.

## Read before changing

- `module.contract.yml`
- `/domain/contexts/classification.md`
- relevant ADRs

## Commands

- targeted module tests
- architecture validation

## Critical rules

- Teams without games remain visible.
- Performance validation is required for query changes.
```

Los hechos estructurales que puedan derivarse del código no se duplican aquí.

---

# 12. Navegación y contexto progresivo

El agente comienza con contexto mínimo:

```text
Task
Root AGENTS.md
Repository revision
Risk and permission policies
Available navigation tools
```

Después localiza y expande:

```text
Minimal bootstrap
→ Locate module and feature
→ Read contract, invariants, ADR, policy, and waivers
→ Inspect observed entry points
→ Expand through dependencies, data, and tests
→ Analyze impact
→ Implement
```

Herramientas recomendadas:

```bash
agentic locate "where is classification calculated?"
agentic symbol ClassificationCalculator
agentic references ClassificationCalculator
agentic tests find ClassificationCalculator
agentic impact src/Modules/Classification/Features/Standings/
agentic data owner ClassificationSnapshots
agentic decisions find "classification ordering"
```

La CLI de referencia incluida expone el subconjunto actual mediante
`python3 tools/architecture/context.py index|locate|symbol|references|tests|impact`.
La búsqueda de símbolos es una observación de texto exacto, no un grafo semántico
de compilador, y la salida declara esa confianza. La búsqueda rica de datos y
decisiones sigue siendo un punto de extensión de los adaptadores.

La salida distingue siempre:

- semántica declarada;
- estructura observada;
- inferencias o heurísticas;
- nivel de confianza;
- revisión del índice utilizada.

El registro de contexto conserva procedencia y motivos, nunca chain-of-thought
privada.

---

# 13. Control y evidencia

Las políticas pueden residir en:

```text
.agentic/policies/
├── architecture/
│   ├── project-policy.json
│   ├── waivers.json
│   └── reviews.json
├── risk-levels.yml
├── permissions.yml
├── quality-gates.yml
└── state-transitions.yml
```

La evidencia de una tarea se liga a una revisión:

```text
.agentic/runtime/evidence/{task-id}/{revision}/
├── manifest.json
├── architecture.json
├── build.json
├── tests.json
├── security.json
├── performance.json
├── review.json
└── unresolved-risks.json
```

Ejemplo:

```json
{
  "taskId": "AG-142",
  "revision": "73a9c45",
  "check": "architecture",
  "tool": "agentic",
  "command": "./tools/scripts/validate-architecture.sh --format json",
  "exitCode": 0,
  "result": "PASS"
}
```

Si cambia la revisión, la evidencia anterior deja de satisfacer el gate.

También se registra evidencia negativa:

- checks no ejecutados y motivo;
- resultados inconclusos;
- tests flaky;
- licencias utilizadas;
- revisiones semánticas pendientes;
- riesgos no resueltos.

Clases de evidencia:

| Clase | Ejemplos |
|---|---|
| Determinista | Build, tests, schema, dependencias |
| Estática | Linter, SAST, análisis de ownership |
| Observacional | Benchmark, trace, métricas |
| Probabilística | Revisión de agente o LLM |
| Declarativa | Afirmación sin prueba |

Una afirmación declarativa nunca satisface por sí sola un gate.

---

# 14. Tests

Los tests se organizan por tipo y después por módulo, feature o host cuando esa
distinción aporte navegación:

```text
tests/
├── Unit/{Module}/{FeatureArea}/
├── Integration/{Module}/{FeatureArea}/
├── Contract/{Module}/
├── Architecture/
├── EndToEnd/{Host}/
├── Performance/{Module}/
├── Security/{Module}/
└── Agentic/
```

No se crean categorías vacías. Un proyecto pequeño puede mantener tests de
varias features directamente bajo `Unit/{Module}` mientras sigan siendo fáciles
de localizar.

Los tests arquitectónicos son producto, no documentación auxiliar. Protegen:

- reglas generales aplicables;
- política específica;
- límites entre módulos y hosts;
- vigencia de licencias;
- correspondencia entre declaración y observación.

---

# 15. Estado arquitectónico acumulativo

Después de cada cambio, el repositorio contiene lo necesario para que otro agente
continúe sin conversaciones anteriores:

```text
Manifiesto general
+ política del proyecto
+ contratos de módulos
+ AGENTS.md
+ dominio e invariantes
+ ADR
+ arquitectura observada
+ tests arquitectónicos
+ licencias
+ evidencia
= estado arquitectónico actual
```

La memoria de una conversación no es fuente de verdad arquitectónica.

---

# 16. Adopción en un repositorio existente

No se realiza una migración masiva únicamente para reproducir esta gramática.

Orden recomendado:

1. inventariar capacidades, hosts y dependencias actuales;
2. declarar política y contratos sin falsear el estado observado;
3. registrar deuda y licencias temporales;
4. proteger primero los límites críticos;
5. reorganizar al tocar cada área o cuando el beneficio justifique una migración;
6. retirar licencias a medida que declaración y observación converjan.

Una arquitectura parcialmente migrada debe informar su estado con `WAIVED` o
`REVIEW_REQUIRED`, no presentarse como completamente conforme.

---

# 17. Contenido de `.agentic`

Solo se materializan las áreas utilizadas:

```text
.agentic/
├── contracts/                # schemas de política, licencias y resultados
├── policies/                 # arquitectura, riesgo, permisos y gates
├── workflows/                # ciclos operativos reutilizables
├── skills/                   # procedimientos especializados
├── prompts/                  # prompts del proceso de ingeniería
├── templates/                # worksheets, handoffs y evidencia
├── generated/                # datos regenerables
├── runtime/                  # estado y trazas
└── evals/                    # experimentos y resultados
```

Los prompts que forman parte del producto viven con la feature propietaria. Los
prompts de ingeniería transversal viven bajo `.agentic/prompts`.

Se versionan normalmente:

- arquitectura y dominio;
- contratos y políticas;
- ADR y licencias;
- workflows, skills y templates;
- schemas, datasets, graders y tooling.

Los índices pueden versionarse o regenerarse según su coste. El estado de runtime,
cachés, trazas y resultados voluminosos se conserva normalmente como artefacto
de CI u observabilidad.

---

# 18. Evaluación falsable

La arquitectura se considera útil solo si mejora resultados medibles frente a
un repositorio convencional.

Condiciones recomendadas:

```text
Baseline
  repositorio convencional + herramientas estándar

Static Context
  estructura + AGENTS.md + contexto inicial fijo

Adaptive Repository
  contratos + índice + navegación progresiva + evidence gates
```

Métricas:

- acceptance tests superados;
- defectos y merge blockers;
- violaciones de scope o módulo;
- tiempo hasta el primer archivo relevante;
- precisión de localización y selección de tests;
- precisión del análisis de impacto;
- falsas declaraciones de completitud;
- tokens, tool calls, coste y duración;
- contexto relevante frente a contexto total.

La búsqueda semántica, MCP y colaboración multiagente son extensiones opcionales.
Se incorporan solo cuando la evaluación demuestra una mejora sobre mecanismos
más simples.

---

# 19. Flujo operativo completo

```text
Petición
  ↓
Bootstrap mínimo
  ↓
Localizar módulo y feature propietarios
  ↓
Leer contrato, invariantes, ADR, política y licencias
  ↓
Comparar arquitectura declarada y observada
  ↓
Extender el límite existente o justificar uno nuevo
  ↓
Implementar
  ↓
Actualizar declaración y enforcement si cambió un límite
  ↓
Ejecutar validaciones de riesgo
  ↓
Conservar evidencia ligada a la revisión
  ↓
PASS / FAIL / WAIVED / REVIEWED / NOT_APPLICABLE / REVIEW_REQUIRED
  ↓
Entrega humana o automatizada según política
```

---

# 20. Decisiones normativas cerradas

1. El manifiesto es un protocolo de decisión, no una plantilla exhaustiva.
2. La arquitectura se crea con necesidades y evidencia actuales.
3. El producto se organiza por capacidades funcionales y features cohesivas.
4. Un comando o caso de uso no crea automáticamente una feature raíz.
5. Los módulos técnicos están prohibidos salvo capacidad y ownership reales.
6. La estructura se materializa bajo demanda; no existen placeholders obligatorios.
7. Un assembly necesita un límite verificable.
8. Lo compartido necesita consumidores actuales y ownership explícito.
9. Los contratos manuales contienen semántica no derivable.
10. La arquitectura declarada se compara con la observada.
11. Las reglas generales, la política del proyecto y las licencias son capas
    distintas.
12. Las licencias son visibles, acotadas y revisables.
13. Un cambio de límite actualiza código, declaración, enforcement y evidencia.
14. Un plan de implementación no puede ignorar la arquitectura silenciosamente.
15. `AGENTS.md` actúa como router, no como enciclopedia.
16. El contexto se recupera progresivamente.
17. La evidencia está ligada a la revisión.
18. Una afirmación del agente no satisface un quality gate.
19. La utilidad de la arquitectura debe ser falsable mediante evaluación.
20. Herramientas complejas se añaden solo cuando demuestran valor.

---

# 21. Criterio final de éxito

El manifiesto cumple su objetivo cuando un agente nuevo puede:

1. crear desde cero la arquitectura mínima justificable con lo que conoce;
2. distinguir lo conocido, lo supuesto y lo pendiente;
3. localizar ownership, módulo y feature para una petición posterior;
4. hacer crecer el proyecto sin anticipar estructura innecesaria;
5. reconocer cuándo un nuevo límite está realmente justificado;
6. actualizar de forma atómica arquitectura declarada y observada;
7. validar reglas generales, decisiones específicas y licencias;
8. identificar código, datos, dependencias y tests afectados;
9. producir evidencia ligada a la revisión;
10. entregar el repositorio a otro agente sin depender de memoria conversacional.

La estructura de carpetas es una consecuencia visible de este protocolo. La
arquitectura real es el conjunto coherente de decisiones, ownership, código,
validaciones y evidencia que permite al repositorio explicar y proteger su propio
crecimiento.
