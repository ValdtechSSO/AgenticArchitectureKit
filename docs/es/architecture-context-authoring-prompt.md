# Prompt para que un agente mantenga el contexto arquitectónico

[English — canonical](../architecture-context-authoring-prompt.md)

Usa este prompt para pedir a un agente que cree, actualice o reconcilie el
contexto arquitectónico mantenido de un proyecto AAK: decisiones de
arquitectura, visión del sistema, invariantes globales y de capacidad, y routers
`AGENTS.md` del repositorio o módulo. El usuario aporta significado y decisiones
materiales, no Markdown, nombres de archivo, anchors ni instrucciones de
navegación.

Esta guía es operativa, no una segunda fuente normativa. El core, las reglas
portables, project policy, contratos de módulo, declaración de autoridad y
decisiones aceptadas de la versión exacta fijada siguen siendo la autoridad.

## 1. Misión y petición mínima del usuario

~~~text
Raíz del repositorio: <DESCUBRIR_DEL_WORKSPACE_O_PROPORCIONAR>
Modo: <BOOTSTRAP_CONTEXT|RECORD_DECISION|UPDATE_SEMANTICS|REFRESH_ROUTING|RECONCILE_DRIFT>
Resultado de producto o arquitectura: <INTENCIÓN_EN_LENGUAJE_NATURAL>
Decisión o invariante conocido: <OPCIONAL_O_UNKNOWN>
Capacidad o scope afectado: <DESCUBRIR_O_UNKNOWN>
Fuente de autoridad: <POLICY_ISSUE_BRIEF_DEL_USUARIO_O_UNKNOWN>

Crea o actualiza solo el contexto mantenido necesario para que un agente nuevo
comprenda la arquitectura actual y pueda actuar con seguridad. El usuario
aporta significado y decisiones, no Markdown. Tú te encargas de descubrir,
seleccionar artefactos, elegir nombres, numeración, headings, anchors, links,
routing, redacción concisa, consistencia, validación e informe final.

No pidas al usuario números de ADR, rutas, headings, anchors, secciones de
plantilla, layouts de AGENTS.md, sintaxis de links ni comandos de validación.
Pregunta solo si continuar exigiría inventar o cambiar materialmente significado
de producto, un invariante, ownership, dirección arquitectónica, riesgo aceptado
o autoridad.
~~~

La petición mínima útil es una frase, por ejemplo: «Registra que la reserva de
stock pertenece a Pedidos y nunca puede ser negativa» o «Prepara el contexto
arquitectónico mínimo del repositorio». Descubre el resto del repositorio y su
autoridad delegada siempre que sea posible.

## 2. Límites de los artefactos

Mantén cada artefacto enfocado:

| Artefacto | De qué es responsable | En qué no debe convertirse |
|---|---|---|
| `architecture/system-overview.md` | Propósito, actores, capacidades, hosts, dirección de dependencias, integraciones y preguntas actuales. | Diario histórico, inventario de archivos o roadmap especulativo. |
| `architecture/decisions/ADR-*.md` | Motivo de una decisión material, scope, alternativas, consecuencias, enforcement y condiciones de revisión. | Descripción del código existente o aprobación fabricada por el agente. |
| `domain/global-invariants.md` | Reglas estables que cruzan capacidades o aplican al sistema completo. | Colección de validaciones locales, preferencias de código o implementación. |
| `domain/contexts/*.md` | Vocabulario, reglas, propiedad e invariantes de una capacidad. | Duplicado del contrato o catálogo generado de clases y entidades. |
| `AGENTS.md` raíz | Router pequeño: propósito, contexto inicial, comandos, límites críticos, mapa y operaciones prohibidas. | Manual de arquitectura, tutorial, changelog o memoria conversacional. |
| `AGENTS.md` de módulo | Router al contrato, dominio, ADR, comandos y reglas locales aplicables. | Duplicado del contrato, instrucciones genéricas o inventario de código. |
| `architecture-discovery.md` | Registro opcional de hechos conocidos, supuestos, incógnitas y límites propuestos durante bootstrap/adopción. | Diseño especulativo permanente o sustituto de decisiones aceptadas. |

La policy declara intención estructural; los contratos declaran semántica estable
del módulo; los adaptadores observan hechos tecnológicos. Los documentos de
contexto explican significado, razones, navegación y restricciones. Ningún
artefacto debe suplantar a otro.

## 3. Descubrimiento obligatorio y clases de evidencia

Antes de escribir:

~~~text
1. Lee las instrucciones del repositorio y ejecuta el gate de arquitectura.
2. Ejecuta y lee `aak core` desde la distribución exacta fijada.
3. Carga DOC001, CHG001, MOD001, MOD002, OWN001, AUT001 y las referencias de
   findings aplicables mediante `aak explain` o sus referencias emitidas.
4. Lee project policy, contratos, contexto actual, ADR, authorities, waivers,
   límites de código, tests y requisitos relevantes. El contexto generado es
   solo evidencia vinculada a una revisión.
5. Clasifica cada afirmación como AUTHORIZED_DECISION, MAINTAINED_SEMANTICS,
   OBSERVED_FACT, INFERENCE, ASSUMPTION o UNKNOWN y registra su fuente.
6. Identifica el consumidor: qué agente futuro, módulo, referencia del validador
   o reviewer necesita el dato y en qué scope mínimo.
7. Detecta contradicciones, contenido obsoleto, links rotos, significado
   duplicado, placeholders y ADR aceptados que el cambio reescribiría.
~~~

Los requisitos y decisiones autorizadas establecen significado. Los contratos y
documentos de dominio mantenidos establecen semántica declarada. El código y el
adaptador muestran implementación. Un patrón observado no es automáticamente un
invariante ni una decisión aceptada.

## 4. Contrato de evidencia de los artefactos

Usa esta matriz para decidir qué escribir:

| Sujeto | Evidencia fiable | Regla de creación | Atajo prohibido |
|---|---|---|---|
| Propósito y actores | Brief actual, scope aceptado, interfaces y usuarios reales. | Expresa lo actual en lenguaje de producto. | No conviertas supuestos o actores posibles en scope. |
| Límites de capacidad | Contratos, policy, vocabulario, ownership, estado, invariantes, lifecycle y decisiones. | Explica por qué cada módulo actual es una capacidad cohesiva. | No derives capacidades de carpetas, capas, frameworks o equipos. |
| Hosts e integraciones | Necesidades actuales de ejecución, ports, sistemas externos y policy. | Describe adaptación, composición y dirección de aislamiento. | No asignes comportamiento al host ni presentes integraciones futuras como actuales. |
| Dirección de dependencias | Decisiones, contratos públicos, permisos y consumidores. | Explica dirección estable y motivo sin copiar cada edge. | No infieras autorización de una dependencia observada. |
| Contexto del ADR | Fuerzas, restricciones, evidencia y problema preciso actual. | Explica por qué hace falta decidir ahora. | No fabriques urgencia ni razones retrospectivas. |
| Decisión y estado del ADR | Autoridad delegada, requisito aceptado o propuesta pendiente. | Usa `proposed` hasta una aceptación real y `accepted` solo con evidencia. | Poder editar no concede autoridad para aceptar. |
| Consecuencias del ADR | Beneficios, costes, riesgos, enforcement, migración y revisión reales. | Incluye consecuencias negativas e impacto operativo. | No ocultes tradeoffs ni uses beneficios genéricos. |
| Alternativas del ADR | Opciones realmente evaluadas. | Registra por qué se rechazaron alternativas plausibles. | No inventes alternativas débiles después. |
| Invariante global | Regla estable que cruza capacidades o aplica a toda operación relevante. | Dale heading único y durable y una obligación precisa. | No promociones una regla local solo para hacerla visible. |
| Invariante de capacidad | Regla explícita propiedad de una capacidad. | Ponla en su contexto y referencia el heading exacto desde el contrato. | No dupliques la prosa en contrato, router, policy y tests. |
| Vocabulario y propiedad | Lenguaje de producto, purpose, datos autoritativos y autoridad de dominio. | Define solo términos necesarios para el trabajo actual. | No infieras ownership de lecturas, tablas, ORM o namespaces. |
| Propósito y mapa del router raíz | Propósito, raíces mantenidas y comandos autoritativos. | Mantén el router pequeño y deriva al contexto profundo. | No enumeres cada archivo o convención. |
| Reglas críticas del router | Límites de seguridad costosos, invariantes, autoridad y gates. | Incluye solo lo necesario antes de actuar. | No copies todo el catálogo portable. |
| Router de módulo | Contrato, contexto estrecho, ADR, comandos y reglas locales. | Enruta localmente y hereda las instrucciones raíz. | No repitas el contrato ni reglas ajenas. |
| Preguntas abiertas | Incógnitas materiales sustentadas por huecos de evidencia. | Déjalas sin resolver y fuera de policy/estructura. | No materialices una incógnita como módulo o abstracción placeholder. |

Cada link de invariante o ADR usado por contrato o policy debe resolver a una
ruta real. Cada anchor de invariante debe corresponder a un heading único y
estable. Prefiere una afirmación autoritativa y links frente a prosa repetida.
Cuando una regla crítica necesite enforcement mecánico nuevo del proyecto,
ejecuta `aak guide project-rule-authoring-prompt`; documentarla no crea un gate.

## 5. Ciclo de vida de decisiones e invariantes

### Decisiones de arquitectura

Crea un ADR solo para una elección material que necesite una razón durable:
crear/unir/dividir capacidades, transferir propiedad, añadir límites de host o
build, cambiar dirección de dependencias, contrato público, estrategia
importante de persistencia/integración, reducción normativa o waiver autorizado.
Cuando un ADR aceptado autorice una desviación temporal de una regla portable,
ejecuta `aak guide waiver-authoring-prompt` para materializar la concesión
acotada; el ADR por sí solo no licencia un hallazgo.

No crees ADR para colocación rutinaria ya determinada. Numera desde la evidencia
del repositorio sin renumerar el historial. Conserva el texto de ADR aceptados
como registro de aquel momento. Si cambia materialmente la dirección, crea un
ADR que lo sustituya y marca el anterior `superseded` con una referencia real.

### Invariantes

Un invariante expresa un resultado que debe mantenerse en todas las operaciones
relevantes, incluidos fallo, retry, concurrencia, migración e interfaces
alternativas cuando corresponda. Colócalo en el scope propietario más estrecho
y usa un heading descriptivo estable, no un anchor basado solo en número.

Cambiar un invariante es una decisión de producto o riesgo, no limpieza de docs.
Si el código lo infringe, corrige la implementación o muestra el conflicto;
nunca debilites el texto para describir el bug.

## 6. Flujo según el modo

### `BOOTSTRAP_CONTEXT`

Construye un registro de conocido, supuesto y desconocido. Crea router raíz y
system overview con evidencia conocida. Crea routers de módulo, contextos,
invariantes y ADR solo donde existan semántica o decisiones actuales reales.
Elimina todos los placeholders. Las incógnitas pueden seguir como preguntas,
pero no convertirse en estructura especulativa.

### `RECORD_DECISION`

Determina si la elección es material y no está ya gobernada. Localiza la
autoridad real, redacta el ADR mínimo, mantén un estado honesto y sincroniza solo
policy, contratos, invariantes, routers, implementación y tests afectados.
Ejecuta `aak guide project-policy-authoring-prompt` o
`aak guide module-contract-authoring-prompt` cuando cambien esos artefactos.

### `UPDATE_SEMANTICS`

Identifica el cambio autorizado y su owner. Actualiza el único invariante o
documento de dominio autoritativo y repara referencias y resúmenes sin
duplicarlo. Conserva el historial con un ADR nuevo cuando cambie una dirección
arquitectónica aceptada.

### `REFRESH_ROUTING`

Actualiza un router solo cuando cambien purpose, ruta de lectura, comandos,
límites críticos, mapa u operaciones prohibidas. Verifica cada comando y link.
Mantén los detalles en su documento propietario y el router suficientemente
breve para leerlo al inicio de una tarea.

### `RECONCILE_DRIFT`

Clasifica cada conflicto antes de editar:

~~~text
IMPLEMENTATION_DRIFT
  corrige código o estructura según la decisión o invariante aceptado

STALE_CONTEXT
  actualiza contexto desde una decisión autorizada más reciente y su implementación

CONTRADICTORY_DECLARATIONS
  identifica el owner autoritativo; no mezcles afirmaciones incompatibles

UNAUTHORIZED_SEMANTIC_CHANGE
  conserva la autoridad actual y pide la decisión material ausente

BROKEN_NAVIGATION
  repara ruta, anchor, comando o router sin cambiar significado

INSUFFICIENT_EVIDENCE
  mantén explícita la incógnita y no la conviertas en arquitectura
~~~

## 7. Gate de intervención del usuario

Continúa autónomamente cuando autoridad y evidencia determinen significado,
scope, ubicación, links y estado. Haz una pregunta breve de producto solo si las
alternativas cambiarían materialmente:

- propósito o propiedad de capacidades;
- un invariante o su scope;
- dirección arquitectónica o riesgo aceptado;
- si una decisión está propuesta o autorizada;
- qué declaración mantenida incompatible es autoritativa;
- autoridad para sustituir una decisión o cambiar una regla protegida.

Recomienda la opción segura más pequeña y explica su consecuencia. Nunca pidas
al usuario escribir Markdown, nombrar archivos, elegir anchors, numerar ADR,
organizar routers ni duplicar información.

## 8. Sincronización atómica y validación

Antes de terminar:

~~~text
1. Comprueba que cada hecho tenga un único hogar autoritativo y que los resúmenes coincidan.
2. Resuelve cada ruta y heading referenciado por policy o contratos; valida DOC001.
3. Verifica números ADR únicos, estado honesto, links de supersession y decisionRefs aplicables.
4. Verifica que los invariantes estén en el scope mínimo, con headings estables,
   y reflejados en tests o evidencia de review donde puedan aplicarse.
5. Verifica todos los comandos y links de los routers AGENTS.md.
6. Elimina placeholders, afirmaciones especulativas, inventarios obsoletos,
   prosa normativa duplicada y referencias a conversaciones.
7. Ejecuta tests afectados, `aak validate`, comparación base estricta cuando
   aplique y `aak context index` tras cambios de navegación.
8. Confirma que un agente nuevo localice owner, significado, límites, comandos y
   razones sin la conversación anterior.
~~~

Que un link resuelva solo demuestra que existe el documento. No demuestra que
un invariante esté autorizado, que un ADR esté aprobado o que un resumen sea
semánticamente correcto.

## 9. Informe final

~~~text
Modo y scope:
Significado o decisión registrados en lenguaje natural:
Fuentes de evidencia y autoridad:
Archivos creados o modificados y motivo:
Hogar autoritativo de cada invariante o decisión:
Estado del ADR, alternativas, consecuencias y triggers de revisión:
Referencias y anchors comprobados:
Routers y comandos comprobados:
Cambios relacionados de policy o contrato:
Decisiones solicitadas al usuario, si existen:
Supuestos e incógnitas mantenidos explícitos:
Comandos y resultados de validación:
Contradicciones o findings FAIL, WAIVED o REVIEW_REQUIRED restantes:
~~~

No declares finalizada la tarea si el contexto contiene placeholders,
aprobaciones fabricadas, cambios semánticos indocumentados, referencias rotas,
fuentes de verdad duplicadas, comandos obsoletos, arquitectura especulativa o
una decisión material que solo existe en la conversación.
