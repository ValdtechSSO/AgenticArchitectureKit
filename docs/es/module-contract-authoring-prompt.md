# Prompt para que un agente cree un contrato de módulo

[English — canonical](../module-contract-authoring-prompt.md)

Usa este prompt para pedir a un agente que cree, adopte o actualice un
`module.contract.yml` de AAK. Sustituye los valores conocidos entre corchetes y
deja como `UNKNOWN` los desconocidos; el agente debe resolverlos mediante
evidencia autorizada del repositorio o preguntar solo por una decisión semántica
material. Esta guía es operativa, no una segunda fuente normativa. El core,
schema, policy y referencias de reglas de la versión fijada siguen siendo la
autoridad.

## 1. Misión e intención proporcionada

~~~text
Root del repositorio: <REPOSITORY_ROOT>
Versión compatible de AAK: <AAK_VERSION>
Modo: <CREATE_NEW_MODULE|ADOPT_EXISTING_MODULE|UPDATE_EXISTING_CONTRACT>
Root del módulo o capacidad propuesta: <MODULE_ROOT_OR_CAPABILITY>
Intención del usuario en lenguaje natural: <WHAT_THE_MODULE_MUST_OWN_AND_ACHIEVE>
Exclusiones conocidas: <WHAT_MUST_NOT_BELONG_TO_THIS_MODULE_OR_UNKNOWN>
Datos o estado conocidos: <KNOWN_OWNED_DATA_OR_UNKNOWN>
Invariantes conocidos: <KNOWN_INVARIANTS_OR_UNKNOWN>
Riesgos conocidos: <KNOWN_RISKS_OR_UNKNOWN>
Fuentes de decisión autorizadas: <PRODUCT_BRIEF_ISSUES_DOCS_ADRS_OR_CONVERSATION>
Autoridad para crear o actualizar documentos de dominio y ADR: <YES|NO>

Crea o actualiza el contrato de módulo más pequeño y veraz sustentado por la
intención y evidencia actuales. El usuario aporta significado, no YAML. Tú eres
responsable del descubrimiento, mapeo de propiedades, identificadores, formato,
conformidad con schema, comprobación de referencias, validación e informe final.

No pidas al usuario que elija propiedades del schema, sintaxis YAML, paths,
anchors, casing del identificador ni comandos de validación. Pregunta solo
cuando continuar inventaría o cambiaría materialmente alcance de producto,
ownership semántico, un invariante, riesgo aceptado, dirección arquitectónica o
autorización.
~~~

La entrada humana mínima puede ser una sola frase: «Crea o actualiza el contrato
de la capacidad responsable de `<INTENT>`». El root, versión fijada, modo, root
del módulo y evidencia existente deben descubrirse desde el contexto de trabajo
siempre que sea posible. Todos los demás campos son opcionales y pueden seguir
como `UNKNOWN` hasta resolverlos mediante evidencia o una decisión autorizada.

## 2. Frontera del contrato

Conserva estas responsabilidades:

~~~text
Usuario o autoridad de producto delegada
  decide significado del producto, ownership, invariantes, riesgo aceptado y
  dirección arquitectónica material

Agente implementador
  descubre evidencia, propone redacción, escribe YAML, mantiene referencias,
  sincroniza artefactos relacionados autorizados y valida el resultado

module.contract.yml
  registra identidad estable, propósito, vocabulario, ownership, riesgo,
  invariantes y referencias de decisiones del módulo

project-policy.json
  declara root del módulo, proyectos observables, roles, namespaces y
  dependencias arquitectónicas permitidas

Adaptador tecnológico
  observa hechos de código y build; no decide ownership semántico
~~~

Código, acceso a base de datos, nombres de carpetas, índices generados y una
policy existente son evidencia, no autoridad semántica automática. Nunca
deduzcas que un módulo posee datos solo porque ahora los lee, escribe, mapea o
almacena. Nunca copies clases, handlers, endpoints, routes, paths, tests o
inventarios de archivos dentro del contrato.

## 3. Contexto y descubrimiento obligatorios

~~~text
Antes de escribir el contrato:

1. Ejecuta y lee desde la distribución exacta fijada:

   aak core
   aak guide bootstrap
   aak template module.contract.yml
   aak validate --list-rules

2. Lee completamente `module-contract.schema.json` empaquetado y carga las
   referencias actuales de MOD001, MOD002, OWN001, DOC001, POL001 y CHG001
   mediante `aak explain` o las referencias emitidas por los findings.

3. Lee `AGENTS.md` del repositorio y módulo, project policy, system overview,
   documentos de dominio y ADR aplicables. En adopción o actualización,
   inspecciona source, tests, acceso a datos, consumidores y límites de build.

4. Clasifica cada input como AUTHORIZED_DECISION, MAINTAINED_DOCUMENT,
   OBSERVED_CODE, INFERENCE o UNKNOWN. Registra su path, anchor, issue o
   declaración del usuario. Los índices generados son evidencia OBSERVED_CODE
   para una revisión concreta.

5. Reconcilia contradicciones antes de escribir. Los documentos semánticos
   mantenidos prevalecen sobre observaciones generadas, pero debes informar de
   documentos obsoletos en vez de copiarlos. Una discrepancia del código puede
   ser un problema de conformidad, no permiso para reescribir el contrato.
~~~

Para un módulo nuevo, verifica que los requisitos actuales justifiquen una
capacidad funcional separada por vocabulario, ownership, invariantes, ciclo de
vida o una frontera exigible. No crees un módulo solo porque exista una
categoría técnica, framework, carpeta o capa.

## 4. Contrato de evidencia de las propiedades

Completa cada propiedad según esta matriz:

| Propiedad | Significado | Evidencia preferida | Atajo prohibido |
|---|---|---|---|
| `id` | Identidad técnica estable de la capacidad. | Id de policy y root existentes; para un módulo nuevo autorizado, deriva un id normalizado del vocabulario de dominio acordado. | No copies un framework, capa, equipo o nombre temporal de proyecto. |
| `name` | Nombre legible de la capacidad. | Vocabulario de producto usado consistentemente en requisitos autorizados y documentos de dominio mantenidos. | No embellezcas un nombre de directorio sin explicación y lo presentes como significado decidido. |
| `purpose` | Descripción concisa de qué posee el módulo y por qué existe. | Intención del usuario, product brief, system overview, contexto de dominio y ADR aplicables. | No describas clases, endpoints, almacenamiento, librerías ni flujo de implementación. |
| `intent.aliases` | Expresiones reales que deben dirigir tareas y preguntas al módulo. | Términos usados por usuarios, expertos, requisitos, issues, comandos y documentación mantenida. Se exige al menos uno. | No generes sinónimos especulativos para alargar la lista. |
| `ownership.domain` | Frontera funcional de la que responde el módulo. | Decisión explícita de ownership de producto o dominio sustentada por vocabulario e invariantes. | No equipares namespace, schema de base de datos, path o equipo con ownership semántico. |
| `ownership.authoritative_data` | Conceptos de datos estables para los que el módulo es fuente de verdad. | Decisión explícita, documentación de dominio, ciclo de vida, autoridad de escritura y responsabilidad para resolver conflictos. Una lista vacía es válida si no se conoce ninguno. | Lecturas, escrituras, tablas, entidades o mappings ORM no prueban ownership. No enumeres archivos ni tipos. |
| `risk.default` | Consecuencia por defecto de los cambios: `low`, `medium`, `high` o `critical`. | Impacto, reversibilidad, durabilidad de datos, seguridad/privacidad, disponibilidad, cumplimiento y policy de riesgo actuales. | No derives el riesgo solo de tamaño, tests, complejidad o confianza del agente. |
| `risk.reasons` | Razones concretas que sustentan el riesgo. | Consecuencias y preocupaciones protegidas en requisitos, invariantes, incidentes, ADR o autoridad explícita. Vacío solo si no existe razón actual. | No uses relleno como «los cambios podrían romper cosas». |
| `invariants` | Referencias del repositorio a reglas que siempre deben cumplirse. | Documentos de dominio autoritativos con anchors exactos y resolubles. Crea o actualiza documentos solo con autorización. Vacío si no hay invariante decidido. | No inventes anchors, dupliques la regla ni conviertas comportamiento actual en invariante de dominio. |
| `architecture_decisions` | Referencias que explican fronteras y elecciones arquitectónicas materiales. | ADR aceptados y aplicables con paths resolubles. Una frontera de módulo nueva normalmente exige decisión autorizada. | No fabriques un ADR, cites uno ajeno ni uses el contrato como su propia justificación. |

El schema demuestra la forma, no la verdad. Un propósito válido como «hace
cosas» sigue siendo inaceptable. En cambio, un array opcional vacío es más
honesto que semántica inventada.

## 5. Registro de evidencia y decisiones

Antes de editar, produce este registro y consérvalo en el informe de la tarea,
no dentro del contrato:

| Propiedad | Valor propuesto | Evidencia y clasificación | Confianza | Decisión necesaria |
|---|---|---|---|---|
| `id` | ... | ... | exact/proposed | yes/no |
| `name` | ... | ... | exact/proposed | yes/no |
| `purpose` | ... | ... | exact/proposed | yes/no |
| `intent.aliases` | ... | ... | exact/proposed | yes/no |
| `ownership.domain` | ... | ... | exact/proposed | yes/no |
| `ownership.authoritative_data` | ... | ... | exact/proposed | yes/no |
| `risk.default` y `reasons` | ... | ... | exact/proposed | yes/no |
| `invariants` | ... | ... | exact/proposed | yes/no |
| `architecture_decisions` | ... | ... | exact/proposed | yes/no |

Continúa sin preguntar cuando la autoridad del repositorio y la intención
proporcionada hagan inequívoca la respuesta. Si una fila material sigue UNKNOWN
o contradictoria, formula una pregunta concisa de dominio que agrupe la decisión
pendiente. Muestra recomendación y consecuencias; nunca pidas al usuario YAML.

## 6. Secuencia de creación

~~~text
1. Determina si la capacidad es nueva, existente, fusionada, dividida o solo un
   área técnica dentro de un módulo existente.
2. Localiza el root y declaración de policy actuales, o propón ambos desde la
   intención autorizada sin materializar estructura especulativa.
3. Construye y reconcilia el registro de evidencia.
4. Resuelve con la persona autorizada únicamente incógnitas semánticas materiales.
5. Redacta usando exactamente las propiedades del schema y lenguaje de dominio
   estable. En actualizaciones conserva el significado válido existente.
6. Resuelve todos los paths y anchors de invariantes y ADR. Si falta una
   referencia necesaria, ejecuta `aak guide architecture-context-authoring-prompt`
   y crea o actualiza el documento solo con autorización; en caso contrario
   informa del bloqueo.
7. Para una frontera nueva o modificada, ejecuta los prompts de project policy
   y contexto arquitectónico, y sincroniza policy, router, documentos de
   dominio, ADR y tests solo hasta donde autorice la misma decisión. Nunca
   cambies policy para silenciar la validación.
8. Revisa el diff buscando inventarios estructurales, significado fabricado,
   referencias obsoletas, prosa duplicada y cambios accidentales de ownership.
9. Ejecuta validación AAK consciente del schema y los checks del proyecto.
10. Devuelve contrato final, resumen semántico en lenguaje natural y registro de
    evidencia. El usuario aprueba significado, no detalles de serialización.
~~~

## 7. Validación y aceptación

El resultado solo está completo cuando pasan los checks aplicables:

- el YAML carga con el subconjunto YAML soportado por AAK;
- cumple el `module-contract.schema.json` exacto fijado;
- contiene las propiedades obligatorias y ninguna adicional;
- `MOD001` encuentra contrato y router local;
- `MOD002` confirma que el id coincide con el root declarado;
- `DOC001` resuelve cada path y anchor de invariantes y ADR;
- `OWN001` no encuentra owners declarados duplicados; cualquier conflicto sigue
  visible y el write access observado no demostrable permanece
  `REVIEW_REQUIRED` hasta gestionarlo bajo autoridad declarada;
- `POL001` y `CHG001` siguen válidas si cambió una frontera de policy;
- pasan `aak validate --fail-on-review` y los checks exigidos, o se informa de
  cada finding restante sin debilitar policy;
- un agente nuevo entiende responsabilidad, vocabulario, ownership, riesgo y
  significado protegido sin leer la conversación anterior.

Una validación correcta no demuestra verdad semántica. Presenta propósito,
ownership, invariantes y riesgo propuestos en lenguaje natural para que una
persona autorizada pueda detectar una suposición errónea.

## 8. Reglas de mantenimiento

Actualiza el contrato cuando cambien propósito estable, vocabulario, ownership,
datos autoritativos, riesgo, invariantes o decisiones rectoras. No lo edites por
refactors rutinarios, nuevas clases, endpoints, handlers, tests, movimientos de
carpetas o librerías internas que conserven esa semántica.

Cuando código y contrato discrepen, clasifica la causa antes de editar:

~~~text
IMPLEMENTATION_DRIFT
  devuelve código o policy al contrato ya autorizado

STALE_CONTRACT
  actualiza el contrato desde una decisión semántica autorizada más reciente

NEW_ARCHITECTURE_DECISION
  registra y autoriza la decisión; después actualiza contrato y artefactos

INSUFFICIENT_EVIDENCE
  mantén visible la incertidumbre y solicita la decisión semántica ausente
~~~

Nunca reescribas historia semántica estable para hacer que la implementación
actual parezca intencionada.

## 9. Informe de finalización

~~~text
Modo y root del módulo:
Versión AAK y schema:
Archivos creados o modificados:
Resumen del módulo en lenguaje natural:
Registro de evidencia por propiedad:
Decisiones solicitadas al usuario, si hubo:
Suposiciones rechazadas o mantenidas como unknown:
Conclusión de ownership y datos autoritativos:
Conclusión de riesgo y razones:
Referencias de invariantes comprobadas:
Referencias ADR comprobadas:
Cambios relacionados de policy/router/documentos:
Comandos de validación y resultados:
Findings FAIL o REVIEW_REQUIRED restantes:
Revisión semántica solicitada a:
~~~

No declares completado mientras existan placeholders, referencias sin resolver,
semántica fabricada, contradicciones silenciosas o decisiones no autorizadas de
ownership, riesgo, invariantes o arquitectura.
