# Guía del equipo

[English — canonical](../team-guide.md) · [Manifiesto](MANIFESTO.md) ·
[Guía de creación para el agente](create-project-from-zero.md)

Esta guía está dirigida a propietarios del proyecto, arquitectos, mantenedores y
revisores que utilizan Agentic Architecture Kit. Explica qué incorpora el kit al
repositorio, por qué existe cada artefacto, quién puede modificarlo y cómo puede
el equipo gobernar el trabajo autónomo de los agentes sin convertirse en un
cuello de botella de aprobaciones.

No es una segunda fuente normativa. El núcleo de decisiones y las referencias
de reglas incluidas son canónicos; el [manifiesto](MANIFESTO.md) explica su
propósito para personas. Esta guía traduce el estándar a la práctica cotidiana.

## 1. Modelo operativo

El kit convierte las decisiones del equipo en contexto persistente y ejecutable:

```text
Intención del equipo
    ↓
Documentos, contratos, ADR y política de arquitectura
    ↓
Navegación e implementación del agente
    ↓
Código y dependencias observadas
    ↓
Validador arquitectónico y tests del proyecto
    ↓
Evidencia ligada a la revisión
```

El objetivo es la autonomía gobernada:

- el equipo decide la dirección del producto, tolerancia al riesgo, ownership y
  autoridad;
- el repositorio hace esas decisiones localizables y verificables;
- el agente resuelve la implementación rutinaria y mantiene la arquitectura
  dentro de esa autoridad;
- las personas intervienen únicamente cuando no se ha delegado una decisión
  material.

El repositorio es la memoria compartida. No hace falta una conversación anterior
con el agente para comprender por qué existe la arquitectura actual.

## 2. Tres clases de información

El repositorio se entiende mejor cuando cada artefacto se clasifica como
portable, específico del proyecto o generado.

### 2.1 Activos portables del kit

Proceden de la distribución fijada `agentic-architecture-kit` y conservan la
misma semántica en todos los proyectos:

```text
CLI y motor de validación
catálogo portable y schemas
plantillas neutrales
adaptadores tecnológicos incluidos
```

Se instalan o ejecutan por versión exacta; no se copian al repositorio
consumidor. El proyecto los consume y no los reinterpreta.

Los cambios de reglas portables pertenecen al kit y deben llegar a los proyectos
como una actualización explícita. Una necesidad específica de un proyecto no
justifica cambiar el significado de una regla portable.

### 2.2 Activos mantenidos por el proyecto

Describen el producto real y evolucionan con él:

```text
AGENTS.md
architecture/
domain/
.agentic/toolchain.json
{raíz-de-módulo}/AGENTS.md
{raíz-de-módulo}/module.contract.yml
.agentic/policies/architecture/project-policy.json
.agentic/policies/architecture/waivers.json
.agentic/policies/architecture/authorities.json
.agentic/policies/architecture/reviews.json
.github/CODEOWNERS
tests/Architecture/
```

Puede actualizarlos una persona o un agente dentro de la autoridad delegada. Los
cambios de política, ownership, ADR, invariantes o licencias son cambios
arquitectónicos y deben ser visibles en la revisión.

### 2.3 Activos observados y generados

Se derivan del código, configuración de build o ejecuciones de validación:

```text
.agentic/generated/
.agentic/runtime/evidence/
```

Pueden contener grafos de proyectos, símbolos, dependencias, relaciones de tests
y resultados de validación. Se regeneran; no se mantienen manualmente.

Los datos generados son evidencia útil, pero no autoridad semántica. Si un
índice no coincide con el código o la revisión actual, está obsoleto.

## 3. Referencia de artefactos

| Artefacto | Propósito | Quién lo mantiene | Qué revisa el equipo |
|---|---|---|---|
| `README.md` | Presenta el producto y sus puntos de entrada habituales | Equipo o agente | Exactitud para nuevos colaboradores |
| `AGENTS.md` raíz | Router pequeño con comandos, mapa, reglas críticas y operaciones prohibidas | Equipo o agente autorizado | Claridad de autoridad y límites de seguridad |
| `architecture/system-overview.md` | Capacidades, hosts, integraciones y dirección de dependencias actuales | Equipo o agente autorizado | Que describa el sistema que existe ahora |
| `architecture/decisions/ADR-*.md` | Registra por qué se tomó una decisión arquitectónica material | Propietario de la decisión; el agente puede redactar | Contexto, alternativas, consecuencias y revisión |
| `domain/global-invariants.md` | Reglas de producto que afectan a varias capacidades | Responsables de producto o dominio; el agente puede actualizar desde requisitos aprobados | Corrección y alcance de cada invariante |
| `domain/contexts/*.md` | Vocabulario e invariantes de una capacidad | Equipo propietario o agente autorizado | Significado de dominio y ownership |
| `AGENTS.md` del módulo | Ruta de lectura, comandos y reglas críticas locales | Equipo propietario o agente autorizado | Que un agente nuevo pueda empezar con seguridad |
| `module.contract.yml` | Propósito, vocabulario, ownership, riesgo, invariantes y ADR no derivables | Equipo propietario o agente autorizado | Verdad semántica, no duplicación estructural |
| `.agentic/toolchain.json` | Fija las versiones del kit, catálogo y extensiones | Owners del repositorio o agente autorizado | Intención de upgrade y reproducibilidad |
| `project-policy.json` | Declara módulos, hosts, proyectos, features y dependencias permitidas | Agente autorizado o responsable de arquitectura | Que un límite nuevo esté justificado, no solo observado |
| `waivers.json` | Registra desviaciones acotadas y autorizadas | Autoridad definida por la política del equipo | Digest de regla, scope, riesgo, autoridad, caducidad y eliminación |
| `authorities.json` | Declara principals, scopes protegidos, ramas y controles requeridos | Owners del repositorio | Coincidencia entre declaración y configuración real de plataforma |
| `.github/CODEOWNERS` | Enruta cambios arquitectónicos protegidos hacia los principals declarados | Owners del repositorio | Un patrón real por scope protegido y ningún override que retire al owner |
| `reviews.json` | Registra una aprobación semántica o atestación de mantenedor individual respaldada por plataforma para huella y commit exactos | Autoridad declarada | Modo, identidad, digest de regla, evidencia, SHA, scope y obsolescencia |
| `rules.json` | Catálogo estable de reglas portables | Mantenedores del kit | Semántica común y compatibilidad entre proyectos |
| Adaptador tecnológico | Convierte estructura tecnológica al modelo observado común | Mantenedor del kit o colaborador del adaptador | Precisión de observación; ninguna decisión de política |
| Tests arquitectónicos | Protegen decisiones específicas que el validador común no expresa | Equipo o agente autorizado | Que protejan comportamiento y no detalles accidentales |
| Resultado del validador | Informa conformidad para una revisión concreta | Generado | Fallos, licencias, revisiones semánticas y revisión Git |

## 4. Qué sucede al crear un proyecto

El agente no comienza copiando un árbol completo. Primero registra qué se conoce,
qué se asume y qué se desconoce; después propone la arquitectura mínima sostenida
por los requisitos actuales.

El equipo debería recibir:

1. una propuesta de capacidades y ownership;
2. únicamente los hosts necesarios actualmente;
3. solo proyectos o packages que impongan un límite real;
4. invariantes y riesgos iniciales;
5. una política que coincida con la estructura creada;
6. un archivo de licencias vacío salvo desviación ya autorizada;
7. validaciones automáticas correctas y revisiones semánticas explícitas.

La propuesta no requiere una reunión cuando la definición inicial del producto
ya delega las decisiones relevantes. Hace falta dirección humana cuando queda
realmente abierta una decisión material de producto, riesgo u ownership.

## 5. Desarrollo rutinario

Para una petición ordinaria, el agente sigue la arquitectura existente:

```text
Localizar módulo propietario
→ Localizar área funcional cohesiva
→ Leer contrato, invariantes, ADR, política y licencias
→ Inspeccionar código, dependencias, datos y tests relevantes
→ Implementar
→ Ejecutar validación dirigida y obligatoria
→ Informar evidencia
```

La mayoría de las peticiones no deberían modificar la política. Añadir una
operación a una feature existente, implementar un puerto, incorporar un test o
cambiar un algoritmo interno suele permanecer dentro de un límite establecido.

El equipo no debería aprobar la ubicación rutinaria de archivos. Esa decisión ya
está delegada mediante el repositorio.

## 6. Cuándo cambia legítimamente la arquitectura

La política evoluciona conforme crece el producto. Algunos casos legítimos:

- una capacidad funcional nueva con vocabulario y ownership independientes;
- un host nuevo necesario para exponer o ejecutar el producto;
- un assembly o package que impone aislamiento de despliegue o dependencia;
- un contrato público nuevo entre módulos actuales;
- la eliminación de una dependencia, módulo, host o licencia obsoleta;
- un área funcional cuyo ciclo de vida se ha vuelto independiente.

Un cambio de límite debe llegar como un cambio coherente:

```text
Implementación
+ política del proyecto
+ contratos o routers de módulo
+ ADR cuando la decisión es material
+ documentos de dominio cuando cambia el significado
+ tests arquitectónicos o soporte del adaptador
+ cambios de licencias cuando corresponda
+ evidencia de validación
```

La política no se modifica solo para hacer desaparecer un fallo del validador.
El agente debe poder indicar el requisito actual y la evidencia que justifican
cada límite nuevo.

## 7. Autoridad del agente e intervención humana

La distinción no es «cambios del agente» frente a «cambios humanos», sino
autoridad delegada frente a no delegada.

### El agente continúa normalmente cuando

- el comportamiento pertenece claramente a un módulo y área funcional;
- el cambio es reversible y respeta los contratos establecidos;
- tests, validación y ADR determinan la implementación correcta;
- una petición autorizada exige claramente un límite nuevo dentro del scope de
  producto y ownership ya delegado;
- puede completar una revisión semántica con evidencia y reglas del repositorio;
- puede retirar una licencia porque se ha cumplido su condición registrada.

### El agente escala cuando

- las alternativas cambian materialmente el comportamiento del producto;
- el ownership se trasladaría entre equipos o capacidades;
- continuar acepta un riesgo no autorizado;
- debe desviarse de una regla portable y no existe autoridad para aprobarlo;
- la petición contradice un invariante o ADR aceptado sin solución compatible;
- requiere autoridad externa, destructiva, financiera, legal, de privacidad o
  seguridad que no se ha concedido.

Una preferencia estética, un nombre menor o un resultado `REVIEW_REQUIRED` no
son automáticamente motivos para preguntar al usuario.

## 8. Interpretar los resultados del validador

| Estado | Significado | Respuesta esperada |
|---|---|---|
| `PASS` | El validador ha demostrado la regla para el scope y revisión actuales | Conservar la evidencia |
| `FAIL` | La arquitectura observada viola una regla o declaración | Corregir código o declaración; no suprimir el check |
| `WAIVED` | Una licencia explícita válida autoriza la desviación | Confirmar que scope y condiciones siguen siendo correctos |
| `REVIEWED` | La autoridad declarada aceptó la huella exacta en un commit alcanzable y aportó evidencia apropiada para su modo | Conservar el acuse; un cambio de evidencia lo dejará obsoleto |
| `NOT_APPLICABLE` | La regla no tiene objeto relevante en el proyecto | Ninguna acción salvo cambio arquitectónico |
| `REVIEW_REQUIRED` | La herramienta no puede demostrar una decisión semántica | El agente o una persona revisa según la autoridad delegada |

`PASS` no afirma que toda la arquitectura sea buena: se aplica a una regla,
scope y revisión. `REVIEW_REQUIRED` tampoco es un fallo; impide presentar una
incertidumbre semántica como certeza mecánica.
El validador local demuestra coherencia del registro, no que GitHub haya aplicado
realmente la aprobación. La protección descrita en
[`github-governance.md`](github-governance.md) aporta esa garantía externa.

El modo `team` usa revisión independiente de CODEOWNER mediante pull request. Un
repositorio realmente mantenido por una sola persona usa `solo-maintainer`, un
único principal y una atestación durable de GitHub creada por esa persona fuera
de `reviews.json`. El modo individual hace explícita la menor independencia; no
es un atajo cuando existe un revisor de equipo disponible.

Modo estricto cuando la política exige resolver toda revisión semántica:

```bash
uvx --from agentic-architecture-kit==0.4.5 aak validate --fail-on-review
```

Para CI o evidencia retenida, se recomienda la salida estructurada:

```bash
uvx --from agentic-architecture-kit==0.4.5 aak validate --format json
uvx --from agentic-architecture-kit==0.4.5 aak validate --base-ref origin/main --task-id CI
```

CI debería usar `--base-ref` cuando pueda comparar con la rama objetivo. Así un
nuevo límite o permiso de dependencia necesita un ADR existente y un agente no
puede obtener verde limitándose a ampliar la policy.

## 9. Gobierno de licencias arquitectónicas

Una licencia no es una lista cómoda de exclusiones. Es una decisión visible del
equipo para aceptar una desviación acotada.

Una buena licencia responde:

```text
¿Qué regla portable afecta?
¿Bajo qué `ruleDigest` exacto se autorizó?
¿Dónde se aplica exactamente?
¿Por qué es necesaria ahora?
¿Qué riesgo se acepta?
¿Quién o qué ADR la autoriza?
¿Cuándo caduca o se revisa?
¿Qué evento permite eliminarla?
```

Los revisores deberían rechazar licencias que:

- cubren todo el repositorio sin necesidad;
- no tienen autoridad o ADR;
- describen conveniencia en lugar de una restricción real;
- carecen de condición de revisión o eliminación;
- redefinen una regla portable para todo el proyecto;
- solo pretenden convertir la validación roja en verde.

Cuando una licencia válida deja de coincidir con una violación, el validador la
señala para revisión y eliminación.

El contrato rechaza un `ruleDigest` ausente. Un digest válido pero modificado
impide aplicar la licencia: la violación original permanece visible y la
concesión requiere revisión bajo la semántica actual.

## 10. Revisar un cambio del agente

### Checklist de cambio rutinario

- ¿Permanece en el módulo y área funcional propietarios?
- ¿Conserva la dirección de dependencias entre módulos y hosts?
- ¿Respeta invariantes y ADR relevantes?
- ¿Existen y pasan los tests necesarios?
- ¿La evidencia corresponde a la revisión examinada?
- ¿Se ha evitado crecimiento estructural no relacionado?

### Checklist de cambio arquitectónico

- ¿Qué requisito actual justifica el límite nuevo o modificado?
- ¿Está explícito el ownership?
- ¿Podría permanecer dentro de un límite cohesivo existente?
- ¿La política describe intención o solo oculta lo observado?
- ¿Código, contratos, ADR, tests y política cambian atómicamente?
- ¿Las dependencias nuevas son mínimas y direccionales?
- ¿La licencia es realmente necesaria, acotada y autorizada?
- ¿Las revisiones semánticas se resolvieron con la autoridad correcta?

### Checklist de calidad del contexto

- ¿Puede un agente nuevo localizar el área propietaria desde el router raíz?
- ¿Los contratos usan vocabulario actual del dominio?
- ¿Resuelven los enlaces a invariantes y ADR?
- ¿Los datos estructurales se derivan en lugar de duplicarse?
- ¿La evidencia generada corresponde a la revisión actual?
- ¿Puede continuar otro agente sin la conversación anterior?

## 11. Errores frecuentes

### Tratar el kit como plantilla de carpetas

Crear todos los directorios opcionales empeora la navegación e inventa límites.
Solo se materializan responsabilidades actuales.

### Editar la política por cada cambio de código

La política describe límites arquitectónicos, no cada archivo o clase. La
mayoría de los cambios no debería modificarla.

### Crear módulos técnicos

`Git`, `Providers`, `Validation` o `Repositories` suelen ser detalles dentro de
un propietario funcional, no capacidades del producto.

### Convertir cada comando en una feature raíz

Los comandos que comparten concepto, estado, invariantes y ciclo de vida
permanecen juntos.

### Tratar datos generados como verdad mantenida

Los índices generados describen una revisión. El ownership semántico permanece
en contratos y política mantenidos.

### Pedir a personas decisiones rutinarias

Si la respuesta ya se deriva de la autoridad del repositorio, el agente decide,
implementa, valida y continúa.

### Permitir que el agente asuma autoridad silenciosamente

La autonomía no permite cambiar la dirección del producto, aceptar riesgo no
delegado o trasladar ownership sin fundamento explícito.

## 12. Actualizar el kit en un proyecto

Los schemas, catálogo, adaptadores y validador portable se tratan como una única
dependencia versionada. No se vendorizan en el repositorio consumidor.

Flujo recomendado:

1. identificar las versiones actual y destino del kit;
2. revisar cambios de reglas y schemas portables;
3. actualizar la versión exacta en `.agentic/toolchain.json` y en CI;
4. migrar la política solo si el schema nuevo lo requiere;
5. apoyarse en la suite de conformidad y procedencia de la distribución publicada;
6. ejecutar la validación arquitectónica del proyecto;
7. revisar nuevos `FAIL` o `REVIEW_REQUIRED`;
8. registrar decisiones materiales de adopción en un ADR.

Nunca se sustituyen estos archivos específicos con plantillas durante una
actualización:

```text
AGENTS.md
architecture/
domain/
src/Modules/*/module.contract.yml
.agentic/policies/architecture/project-policy.json
.agentic/policies/architecture/waivers.json
```

Las plantillas sirven para inicialización y referencia, no para upgrades.

## 13. Gobierno recomendado para el equipo

Un acuerdo operativo ligero es suficiente:

- responsables de producto o dominio aprueban invariantes y cambios materiales;
- responsables de arquitectura aprueban cambios de ownership y licencias;
- los agentes pueden mantener política y ADR al implementar trabajo autorizado;
- los revisores exigen evidencia, no ceremonias adicionales;
- CI ejecuta las validaciones automáticas;
- las revisiones semánticas se asignan según riesgo y autoridad;
- el equipo retira periódicamente licencias y decisiones obsoletas.

El objetivo no es centralizar el permiso arquitectónico. Es hacer persistentes
las decisiones para que el trabajo rutinario deje de necesitar permiso.

## 14. Primera revisión de un proyecto generado

Cuando un agente crea un repositorio con el kit, una persona puede revisarlo en
este orden:

1. leer `AGENTS.md` raíz para propósito, comandos y límites críticos;
2. leer `architecture/system-overview.md` para capacidades y hosts;
3. revisar `domain/global-invariants.md` y contextos de capacidad;
4. revisar cada `module.contract.yml` para vocabulario, ownership y riesgo;
5. revisar `project-policy.json` para módulos, proyectos y dependencias;
6. confirmar que `waivers.json` está vacío o cada licencia está autorizada y
   ligada al `ruleDigest` actual;
7. ejecutar la versión exacta declarada en `.agentic/toolchain.json` con `aak validate`;
8. revisar todos los resultados `FAIL`, `WAIVED` y `REVIEW_REQUIRED`;
9. confirmar que pasan el build y los tests del proyecto;
10. confirmar que otro agente podría continuar solo con el repositorio.

Si estas comprobaciones se cumplen, el repositorio no está simplemente ordenado
según un estilo. Contiene un acuerdo ejecutable entre el equipo y los agentes que
lo harán evolucionar.
