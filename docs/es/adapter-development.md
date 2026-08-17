# Cómo escribir un adaptador tecnológico

[English — canonical](../adapter-development.md)

Un adaptador tecnológico observa hechos del repositorio para un lenguaje o
sistema de build. No decide si la arquitectura es válida: las reglas portables
siguen perteneciendo a Agentic Architecture Kit.

## 1. Crea una distribución separada

Construye el adaptador como un package Python con versionado independiente. Fija
la versión compatible del kit y registra un nombre de adaptador en minúsculas:

```toml
[project]
name = "aak-rust-adapter"
version = "0.1.0"
dependencies = ["agentic-architecture-kit==0.4.6"]

[project.entry-points."agentic_architecture_kit.adapters"]
rust = "aak_rust_adapter:observe"
```

El nombre del entry point debe cumplir `[a-z][a-z0-9_]*` y coincidir con el
valor `adapter` de la policy consumidora. Solo puede haber un entry point
instalado con ese nombre.

## 2. Implementa el contrato de observación

El entry point es un callable con este contrato:

```python
from pathlib import Path

from agentic_architecture_kit.model import (
    ObservedArchitecture,
    Project,
    SourceDependency,
    SourceNamespace,
)


def observe(root: Path, policy: dict) -> ObservedArchitecture:
    config = policy.get("adapterConfig", {})
    # Lee manifests y fuentes bajo root. Nunca escribas en el repositorio.
    projects = (
        Project(
            path="crates/planning/Cargo.toml",
            name="planning",
            references=(),
            namespaces=("planning",),
        ),
    )
    return ObservedArchitecture(
        modules=("crates/planning",),
        hosts=("crates/cli",),
        projects=projects,
        source_files=("crates/planning/src/lib.rs",),
        source_dependencies=(
            SourceDependency(
                source_path="crates/planning/src/lib.rs",
                source_namespace="planning",
                target_namespace="contracts",
                kind="use",
                confidence="exact",
            ),
        ),
        directories=("crates/planning/src",),
        source_namespaces=(
            SourceNamespace(
                source_path="crates/planning/src/lib.rs",
                namespace="planning",
                project_path="crates/planning/Cargo.toml",
                confidence="exact",
            ),
        ),
    )
```

Los valores estáticos solo ilustran el modelo. Un adaptador real los deriva de
los manifests y archivos fuente actuales.

## 3. Rellena el modelo con honestidad

- `modules` y `hosts` son raíces observadas relativas al repositorio.
- `Project.path` es el manifest o proyecto de build relativo al repositorio;
  `references` contiene rutas exactas a otros proyectos observados.
- `role_hint="test"` solo se usa cuando el metadata de build u otra señal
  mecánica demuestra ese rol.
- `root_namespace` y `namespaces` describen identidades de import declaradas por
  un proyecto. Si el lenguaje no tiene namespaces, usa la identidad estable de
  package, crate o módulo empleada en los imports.
- `source_files` enumera los fuentes relevantes.
- `SourceNamespace` asocia una identidad declarada con su fuente y, cuando se
  conoce, con su proyecto.
- `SourceDependency` registra una arista dirigida a nivel de fuente. `kind`
  nombra la construcción observada, como `use`, `import` o `require`.
- `directories` aporta observación estructural a las reglas portables.

Todas las rutas usan formato POSIX relativo al repositorio, nunca salen de
`root` y excluyen código generado, vendor, cachés y resultados de build. Devuelve
tuplas ordenadas para que el digest sea determinista. Usa `confidence="exact"`
para hechos parseados y un valor de confianza menor y claro para heurísticas.

## 4. Mantén la policy y las reglas fuera del adaptador

El adaptador puede leer `roots`, `projectSearchRoots`, `structureSearchRoots` y
su `adapterConfig` específico. No debe:

- escribir policy, waivers, reviews, contratos ni código fuente;
- inventar módulos de una estructura futura deseada;
- permitir o rechazar una dependencia;
- redefinir `DEP001`, `DEP002` ni otra regla portable;
- convertir evidencia ausente o ambigua en una observación supuestamente exacta.

Cuando la tecnología no pueda demostrar un hecho, omítelo o refleja su confianza
con honestidad. El validador decide si ese hueco es `NOT_APPLICABLE`,
`REVIEW_REQUIRED` o un fallo.

## 5. Configura un repositorio consumidor

Instala la distribución junto al kit fijado. Añádela a
`.agentic/toolchain.json` para que cualquier deriva de versión bloquee la
validación:

```json
{
  "version": 1,
  "distribution": "agentic-architecture-kit",
  "toolVersion": "0.4.6",
  "catalogVersion": 2,
  "extensions": [
    {"distribution": "aak-rust-adapter", "version": "0.1.0"}
  ]
}
```

La policy selecciona el mismo nombre de entry point y deja los ajustes de
observación específicos bajo `adapterConfig`:

```json
{
  "adapter": "rust",
  "adapterConfig": {"workspaceManifest": "Cargo.toml"},
  "roots": {"modules": "crates", "hosts": "apps"},
  "projectSearchRoots": ["crates", "apps"],
  "structureSearchRoots": ["crates", "apps"]
}
```

Ese fragmento no es una policy completa: parte de
`aak template project-policy.template.json` y valida el documento completo.
`aak validate` carga adaptadores externos. La detección automática y la
generación de policy observada de `aak init` y `aak adopt` cubren actualmente
los adaptadores incluidos, así que la policy inicial de uno externo debe
prepararse y revisarse explícitamente.

## 6. Prueba la observación y la detección de fallos

Usa un repositorio fixture mínimo y prueba:

1. módulos, hosts, proyectos, identidades y aristas exactos;
2. resultado determinista en ejecuciones repetidas;
3. exclusión de build, cachés y vendor;
4. manifests inválidos y rutas que salen del repositorio;
5. una mutación negativa por cada regla automática alimentada por la nueva
   observación.

Instala la extensión en el entorno de test para ejercitar también el
descubrimiento del entry point y ejecuta `aak validate` con una policy completa.
Incluye al menos una arista de fuente prohibida sin referencia de proyecto: un
resultado verde debe demostrar que el adaptador miró, no solo que no devolvió
aristas.

## 7. Lista de comprobación para publicar

- El package del adaptador y la versión compatible del kit tienen pins exactos.
- El nombre del entry point es único y coincide con la policy.
- La observación es de solo lectura, determinista, acotada al repositorio y
  factual.
- Toda ruta y referencia a proyecto resuelve dentro del fixture.
- La evidencia exacta y la heurística usan valores de confianza distinguibles.
- Los fixtures positivos y negativos pasan con `--fail-on-review` según lo
  previsto.
