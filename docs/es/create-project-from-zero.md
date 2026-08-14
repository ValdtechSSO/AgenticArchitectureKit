# Crear o evolucionar un proyecto con Agentic Architecture Kit

[English — canonical](../create-project-from-zero.md) · [Política lingüística](language-policy.md)

Esta es la versión web de la guía versionada que imprime
`aak guide bootstrap`. El agente ejecuta `aak core` y lee completamente ese
núcleo preventivo antes de decidir estructura. Los detalles del validador se
cargan mediante referencias de hallazgos o `aak explain`, no leyendo un
manifiesto completo.

En un repositorio existente se ejecuta el gate antes de la primera modificación.
En uno nuevo, la inicialización y la declaración mínima son escrituras de
bootstrap; el gate se ejecuta inmediatamente después y antes de crear estructura
o implementación de producto. Se repite antes de finalizar.

## 1. Entradas obligatorias

Antes de crear código o carpetas, el agente reúne:

- propósito y alcance actual del producto;
- actores y operaciones conocidas;
- datos, ownership e invariantes conocidos;
- interfaces externas requeridas;
- lenguaje, runtime y restricciones de despliegue;
- riesgos conocidos;
- comandos de build y test disponibles.

Cada dato se clasifica como `KNOWN`, `ASSUMED` o `UNKNOWN`. Un supuesto o una
incógnita no se materializa como módulo, assembly, abstracción o carpeta.

## 2. Descubrir la arquitectura mínima

El agente identifica capacidades por vocabulario, ownership, reglas y ciclo de
vida. Comienza con un solo módulo salvo que la evidencia actual justifique varios.

Para cada posible límite pregunta:

```text
¿Tiene vocabulario propio?
¿Posee datos o estado?
¿Tiene invariantes propios?
¿Evoluciona de forma independiente?
¿Necesita un contrato con otra capacidad actual?
```

Los hosts se derivan únicamente de formas actuales de ejecutar o exponer el
producto. Un proyecto compilable separado necesita un límite verificable de
dependencia, despliegue, runtime, lenguaje, publicación u ownership.

## 3. Proponer antes de materializar

El agente presenta una decisión inicial que incluya:

- módulos propuestos y evidencia de cada límite;
- áreas funcionales cohesivas dentro de cada módulo;
- hosts actuales;
- proyectos o packages necesarios y el límite que imponen;
- dependencias permitidas;
- invariantes, riesgos y ADR iniciales;
- supuestos y preguntas todavía abiertas;
- comprobaciones automáticas y revisiones semánticas necesarias.

Si el usuario ya autorizó crear el proyecto, esta propuesta puede formar parte
del registro arquitectónico y el agente continúa sin pedir confirmaciones
innecesarias. Una decisión que cambie significativamente el producto, el riesgo
o el ownership sí requiere dirección.

## 4. Instalar la base ejecutable

Elige una versión publicada y ejecútala directamente, preferiblemente con
`uvx`. El ejemplo siguiente presupone que `aak` resuelve a esa versión exacta:

```bash
aak init --root . --codeowner @tu-org/architecture
```

El inicializador crea `.agentic/toolchain.json`, registros de gobernanza vacíos
y cobertura CODEOWNERS para todo el repositorio. También escribe una propuesta
observada de `project-policy.json`. Si todavía no existen artefactos tecnológicos,
se indica `--adapter dotnet` o `--adapter python`. No copia al proyecto el motor,
catálogo, schemas, guías ni plantillas portables.

`aak template` enumera las plantillas neutrales de la distribución seleccionada
y `aak template NAME` muestra una. Después se materializan solo los elementos
aplicables:

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

Las rutas opcionales se omiten si no tienen contenido actual.

## 5. Revisar la propuesta de política específica

El inicializador escribe la propuesta observada en:

```text
.agentic/policies/architecture/project-policy.json
```

El agente conserva los hechos que sean límites intencionales, elimina estructura
accidental y añade la semántica decidida que el adaptador no puede inferir:

- raíces de módulos y hosts;
- áreas funcionales existentes;
- proyectos observables y sus owners;
- roles de aplicación, infraestructura, contratos y host;
- dependencias permitidas;
- rutas fuente autorizadas dentro de cada host;
- nombres técnicos o catch-all prohibidos.

La política declara intención. El adaptador obtiene la estructura observada. El
validador compara ambas; la política nunca debe escribirse para ocultar una
violación general.

## 6. Adaptadores tecnológicos

Si existe adaptador incluido para la tecnología, se usa tal cual. Si falta, se
crea una distribución Python versionada que exponga un entry point del grupo
`agentic_architecture_kit.adapters`:

```toml
[project.entry-points."agentic_architecture_kit.adapters"]
technology = "my_aak_adapter:observe"
```

El adaptador solo descubre módulos, hosts, proyectos, dependencias y archivos
fuente. No decide qué arquitectura es válida ni redefine reglas. Su distribución
y versión exacta se fijan en `.agentic/toolchain.json`.

## 7. Licencias

`waivers.json` comienza vacío. Una licencia solo se añade cuando existe una
desviación concreta y autorizada. Debe identificar regla, `ruleDigest` actual,
scope, decisión, motivo, riesgo, ADR autorizador y condiciones de revisión. Su
resultado será `WAIVED`, nunca `PASS`. Un digest ausente u obsoleto impide
aplicarla.

## 8. Autoridad y revisiones semánticas

Sustituye los principals de la plantilla por usuarios o equipos reales y
refléjalos en `.github/CODEOWNERS`. Ejecuta `aak guide github-governance` y
configura cada rama protegida declarada según esa guía versionada. Un review
requiere huella exacta, SHA completo y ancestro alcanzable, principal declarado,
evidencia de aprobación de la plataforma y `ruleDigest` actual. El agente no
debe crear un review solo porque pueda editar JSON.

Elige el modo de autoridad según el ownership real del repositorio:

- `team` exige aprobación independiente de CODEOWNER mediante pull request y es
  el modo predeterminado;
- `solo-maintainer` exige exactamente un principal declarado y una URL durable
  de atestación del mantenedor en GitHub. Conserva pull requests, checks
  obligatorios y ausencia de pushes directos, pero no finge que la auto-review
  sea independiente.

Inicializa un repositorio individual con `--authority-mode solo-maintainer`. No
uses ese modo únicamente para evitar a un revisor de equipo disponible.

## 9. Bootstrap y expansión del contexto

Se genera el índice inicial con `aak context index`.
`locate` ofrece el punto de partida declarado y `references`, `tests` e `impact`
permiten ampliar el contexto conservando procedencia y confianza.

El proyecto debe proporcionar al agente un contexto inicial pequeño y
determinista:

```text
Petición
AGENTS.md raíz
Revisión del repositorio
Políticas de riesgo y permisos
Comandos autoritativos de build, test y arquitectura
```

Después, el agente localiza el módulo y área funcional propietarios, lee el
contrato del módulo, invariantes, ADR, política del proyecto y licencias, y
amplía únicamente mediante dependencias, consumidores, acceso a datos, tests o
huecos concretos de evidencia. Registra la procedencia y distingue hechos
declarados, hechos observados, inferencias y preguntas abiertas. La memoria de
la conversación nunca es necesaria para continuar el trabajo.

## 10. Validación de cierre

El proyecto inicial no está completo hasta ejecutar:

```bash
aak validate
aak validate --base-ref origin/main --fail-on-review
```

`aak explain RULE_ID` muestra hallazgos, scopes, evidencia, digest, referencia y
waiver o review aplicado. Si una referencia normativa no resuelve, la validación
falla; el agente no infiere su posible significado.

La suite de conformidad de la distribución se ejecuta antes de publicarla; los
consumidores no la copian ni la repiten. Además se ejecutan el build, los tests
propios y los tests arquitectónicos específicos del proyecto. Los resultados
`REVIEW_REQUIRED` se enumeran y se revisan; no se presentan como verificaciones
automáticas superadas. Una revisión semántica dentro de la autoridad ya delegada
no requiere por sí sola interacción con el usuario.

La aceptación se persiste en `reviews.json` con la huella exacta emitida; no se
suprime el hallazgo ni se presenta como un pass mecánico.

## 11. Evolución posterior

Cada petición futura vuelve a localizar primero el módulo y área funcional
propietarios. Solo crea un nuevo límite cuando la nueva evidencia lo justifica.
Si cambia un límite, el cambio actualiza conjuntamente código, política,
contratos, ADR, validaciones, licencias y evidencia.

El agente actualiza la política conforme crece el proyecto, pero nunca solo para
hacer desaparecer un fallo:

- un límite nuevo legítimo actualiza la política y la decisión que lo sustenta;
- una violación accidental se corrige en el código;
- una desviación necesaria y autorizada crea una licencia visible;
- la semántica no resuelta permanece como `REVIEW_REQUIRED`.

CI suministra `--base-ref` para comparar el crecimiento de policy con la rama
objetivo. Un nuevo límite o permiso de dependencia sin referencia a una decisión
existente falla aunque el código pudiera quedar verde.

La conversación del agente no es memoria arquitectónica. Al finalizar, otro
agente debe poder continuar leyendo únicamente el repositorio y la distribución
fijada.
