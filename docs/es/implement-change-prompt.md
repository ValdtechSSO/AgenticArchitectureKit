# Prompt para que un agente implemente un cambio de producto

[English — canonical](../implement-change-prompt.md)

Usa este prompt como puerta de entrada predeterminada para crear o evolucionar
un producto con Agentic Architecture Kit. El usuario describe el resultado
deseado en lenguaje natural. El agente implementador se responsabiliza de la
clasificación arquitectónica, descubrimiento, planificación, código, artefactos
mantenidos, validación e informe.

Esta guía coordina instrucciones especializadas de AAK; no sustituye el core,
schemas, policies, contratos, referencias de reglas ni autoridad fijados.

## 1. Petición mínima del usuario

~~~text
Root del repositorio: <DISCOVER_FROM_WORKSPACE_OR_SUPPLY>
Resultado de producto solicitado: <PLAIN_LANGUAGE_REQUEST>
Criterios de aceptación: <OPTIONAL_OR_UNKNOWN>
Restricciones conocidas: <OPTIONAL_OR_UNKNOWN>

Implementa completamente el resultado solicitado. Determina su owner
arquitectónico actual y el cambio mínimo justificado. Mantén artefactos AAK solo
cuando cambien su significado estable o las fronteras declaradas. Pregúntame
únicamente por una decisión material de producto, ownership, invariantes, riesgo,
efectos externos o autoridad que no pueda resolverse desde el contexto delegado
del repositorio.
~~~

La petición mínima útil es una frase, por ejemplo: «Notifícame cuando un vino
guardado vuelva a estar disponible». No exijas al usuario mencionar módulos,
features, contratos, policies, adaptadores, proyectos, ADR, schemas, carpetas,
clases ni comandos de validación.

## 2. Preflight obligatorio

Antes de planificar o editar:

~~~text
1. Lee las instrucciones del repositorio y ejecuta el gate arquitectónico previo.
2. Ejecuta y lee `aak core` desde la versión exacta fijada por el repositorio.
3. Localiza módulo owner y feature area cohesiva mínima usando contratos, policy,
   vocabulario de dominio, source, consumidores y tests mantenidos.
4. Lee únicamente contrato, router local, invariantes, ADR, policy, waivers y
   referencias de findings aplicables.
5. Inspecciona código, ciclo de datos, interfaces, dependencias, tests y cobertura
   de observación tecnológica del comportamiento solicitado.
6. Clasifica la evidencia como DECLARED, OBSERVED, INFERRED, ASSUMED o UNKNOWN.
7. Registra la revisión y una referencia base adecuada para detectar crecimiento
   arquitectónico.
~~~

No empieces creando un módulo, proyecto, capa, abstracción o directorio. Amplía
el owner cohesivo existente salvo que la evidencia actual demuestre que hace
falta una frontera nueva.

## 3. Algoritmo de clasificación del cambio

Clasifica la petición en la primera categoría mínima que la satisfaga:

| Clasificación | Cuándo usarla | Consecuencia arquitectónica |
|---|---|---|
| `ROUTINE_EXISTING_FEATURE` | El comportamiento pertenece a una capacidad y feature owner existentes. | Cambia implementación y tests. Policy, contrato y ADR normalmente permanecen iguales. |
| `NEW_FEATURE_AREA` | Pertenece a un módulo existente, pero tiene vocabulario, estado, invariantes, riesgo, ownership o lifecycle independientemente significativos dentro de él. | Añade el área cohesiva mínima. Si cambia la policy, ejecuta `aak guide project-policy-authoring-prompt`. |
| `MODULE_SEMANTICS_CHANGED` | Cambió propósito estable, vocabulario, ownership, datos autoritativos, riesgo, invariantes o decisiones rectoras del módulo. | Ejecuta el prompt de contrato y, si cambian contexto o fronteras, los prompts de contexto arquitectónico y project policy. |
| `NEW_MODULE` | Una capacidad funcional actual tiene vocabulario y ownership independientes, normalmente con estado/invariantes/lifecycle propios, y no cabe de forma cohesiva en un módulo existente. | Ejecuta los prompts de contrato, project policy y contexto arquitectónico; crea una frontera coherente y su implementación. |
| `NEW_HOST` | Una forma actualmente necesaria de ejecutar, programar, componer o exponer el producto requiere una frontera propia de runtime/adaptación. | Ejecuta los prompts de project policy y contexto arquitectónico; declara host, source mínimo, decisión y dependencias. |
| `NEW_BUILD_UNIT` | Un proyecto/paquete separado hace exigible una frontera de dependencia, despliegue, runtime, lenguaje, publicación, distribución u ownership. | Ejecuta `aak guide project-policy-authoring-prompt`; añade solo unidad observada, owner, role, decisiones y edges autorizados. |
| `NEW_DEPENDENCY_PERMISSION` | El diseño requiere una dependencia nueva entre owners o unidades declaradas. | Ejecuta `aak guide project-policy-authoring-prompt`; prefiere contrato público y autoriza solo el edge exacto o escalable respaldado por una decisión. |
| `TECHNOLOGY_OBSERVATION_GAP` | El adaptador no puede observar con fiabilidad hechos necesarios. | Ejecuta `aak guide adapter-authoring-prompt`; amplía observación sin cambiar reglas portables ni ocultar incertidumbre. |
| `PROJECT_RULE_EXTENSION` | Se necesita una garantía estable de proyecto fuera de las reglas portables actuales. | Ejecuta `aak guide project-rule-authoring-prompt`; implementa evidencia, evaluator/analyzer, tests negativos, excepciones y enforcement local/CI sin sobrecargar la policy. |

Una petición puede tener clasificación primaria y consecuencias secundarias
necesarias. No conviertas mecánicas secundarias en arquitectura independiente.
Por ejemplo, un endpoint nuevo suele pertenecer a una feature existente; no se
convierte automáticamente en feature root, módulo, host o proyecto.

## 4. Gate de decisión para un módulo nuevo

Crea un módulo solo cuando la evidencia actual sustente una capacidad de
producto separada. Construye este registro antes de materializarla:

~~~text
Capacidad propuesta y vocabulario real de dominio:
Módulo existente considerado primero:
Por qué el módulo existente perdería cohesión:
Ownership o autoridad independientes:
Estado o datos autoritativos propios:
Invariantes o riesgo independientes:
Lifecycle o presión de evolución independientes:
Consumidores actuales y contrato público necesario:
Frontera de build/despliegue necesaria, si existe:
Fuente de decisión y autoridad:
Justificación únicamente técnica rechazada:
~~~

Una frontera fuerte de ownership puede bastar. Varias señales débiles de nombres
o carpetas no. `Services`, `Infrastructure`, `Persistence`, `Validation`, un
framework, una base de datos o un equipo no son módulos de producto salvo que
formen una capacidad de plataforma con ownership, contrato y lifecycle propios.

Si la evidencia no justifica la frontera, implementa dentro del módulo existente
y no registres un módulo especulativo. Si siguen siendo válidas dos opciones de
ownership materialmente distintas y la autoridad no delegó una, formula una sola
pregunta de dominio con recomendación y consecuencias.

## 5. Reglas para actualizar la policy

Trata `project-policy.json` como intención declarada comprobada contra la
observación, no como inventario copiado automáticamente del árbol actual.

Cuando el plan contenga un delta de policy distinto de `NONE`, ejecuta
`aak guide project-policy-authoring-prompt` y sigue su registro de evidencias,
reconciliación por modo, autorización y validación. La tabla siguiente entrega
la clasificación; no sustituye esa guía.

Usa esta tabla de decisión:

| Cambio | Acción sobre la policy |
|---|---|
| Comportamiento rutinario, refactor, handler, endpoint, test, adaptador interno o librería interna | Ningún cambio salvo que cambie realmente una frontera declarada. |
| Feature area nueva dentro de un módulo | Actualiza `featureRoot` o `featureAreas` únicamente si la policy actual gobierna esos conceptos y el área está justificada. |
| Módulo nuevo | Añade `id` estable, `root` real, declaración opcional de feature, patrones de identidad sustentados por evidencia y referencias de decisión aplicables. |
| Host nuevo | Añade `id`, `root`, patrones permitidos de adaptación/composición, identidades cuando sean observables y decisiones. |
| Unidad de build nueva | Añade path y nombre observados, owner semántico, role demostrado mecánicamente, contrato público cuando corresponda y decisiones. |
| Dependencia nueva de proyecto/source | Añade permiso solo después de validar dirección, owner, role, contrato público, necesidad y autoridad. Observarla nunca la autoriza. |
| El adaptador descubre estructura existente inesperada | Corrige código/estructura accidental, declara una frontera ya intencionada con evidencia o conserva el finding. Nunca amplíes policy solo para obtener PASS. |

El agente deriva valores mecánicos del adaptador y repositorio. Deriva mappings
semánticos de intención autorizada y decisiones mantenidas. El usuario nunca
rellena JSON. Si una frontera nueva es material, registra un ADR resoluble u otra
decisión aceptada antes de depender del permiso.

Al crear un módulo, actualiza atómicamente según corresponda:

~~~text
implementación
+ module.contract.yml
+ router AGENTS.md del módulo
+ invariantes o contexto de dominio
+ decisión arquitectónica
+ modules/projects/dependencies de project-policy
+ tests arquitectónicos o cobertura del adaptador
+ contexto generado y evidencia de validación
~~~

No crees una unidad de build separada solo porque existe un módulo. No añadas
permiso para una dependencia que la implementación elegida pueda evitar.

## 6. Gate de intervención del usuario

Continúa autónomamente cuando resultado, autoridad del repositorio, contratos,
invariantes y decisiones aceptadas determinen una respuesta segura.

Pregunta al usuario solo si una elección pendiente cambiaría materialmente:

- comportamiento de producto o criterios de aceptación;
- qué capacidad posee comportamiento o datos autoritativos;
- un invariante de dominio;
- riesgo aceptado de seguridad, privacidad, cumplimiento, durabilidad,
  disponibilidad o efecto irreversible;
- una acción externa que requiere autoridad nueva;
- crear, fusionar, dividir o transferir una frontera funcional real;
- permitir una dependencia que cambie la dirección arquitectónica.

No preguntes por YAML, JSON, campos de schema, identificadores, patrones de
namespace/package, ubicación, manifests, parser, layout de tests ni comandos
cuando sean derivables. Agrupa incógnitas relacionadas en una pregunta concisa,
recomienda la opción segura mínima y explica su consecuencia.

## 7. Contrato del plan de implementación

Antes de implementar, produce un plan breve sustentado por evidencia:

~~~text
Resultado solicitado y criterios de aceptación:
Módulo owner y feature area actuales:
Clasificación primaria:
Decisión de frontera y evidencia:
Alcance de implementación y tests:
Delta del contrato: <NONE|SUMMARY>
Delta de policy: <NONE|SUMMARY>
Delta de ADR/invariantes: <NONE|SUMMARY>
Delta de adaptador/extensión de reglas: <NONE|SUMMARY>
Checks de riesgo y autoridad:
Comandos de validación, incluida comparación base:
Única decisión material pendiente, si existe:
~~~

Si el usuario pidió implementación y ninguna decisión material bloquea, no te
detengas tras el plan. Ejecútalo, limita los cambios y revisa el plan si la
evidencia invalida una suposición.

Cuando `Delta de ADR/invariantes` no sea `NONE`, o deba cambiar system overview
o un router, ejecuta `aak guide architecture-context-authoring-prompt`. Coloca
cada decisión o invariante en un único scope autoritativo y repara referencias
sin pedir al usuario que escriba Markdown.

Cuando `Delta de adaptador/extensión de reglas` incluya una garantía propia del
proyecto, ejecuta `aak guide project-rule-authoring-prompt`. El check del
proyecto y la validación AAK permanecen separados salvo que se amplíe
deliberadamente toda la ruta común de modelo, evaluator, catálogo y conformidad.

## 8. Ejecución y atomicidad

Implementa el resultado vertical más pequeño que satisfaga los criterios
actuales. Mantén comportamiento en su capacidad y feature cohesiva, significado
de dominio independiente de infraestructura, contratos públicos limitados a
consumidores actuales, infraestructura tras ports propios y hosts limitados a
adaptación y composición.

En cambios arquitectónicos, código y declaraciones aterrizan juntos. No dejes
policy describiendo archivos inexistentes, fronteras observadas sin declarar,
contratos apuntando a documentos ausentes ni ADR describiendo intención no
implementada. No uses waiver o review para ocultar errores de implementación.

Conserva cambios ajenos. Evita output generado o vendor salvo que una herramienta
obligatoria lo gestione. Actualiza índices y evidencia retenida únicamente con
sus generadores autoritativos.

## 9. Bucle de validación y corrección

Valida en proporción al cambio:

~~~text
1. Tests dirigidos del comportamiento cambiado.
2. Tests de módulo, contrato, integración y arquitectura afectados.
3. Build, lint, tipos, migraciones o paquetes exigidos.
4. `aak validate` para concordancia del estado actual.
5. `aak validate --base-ref <TARGET_BASE> --fail-on-review` para crecimiento y
   finalización estricta.
6. `aak context index` si cambiaron fronteras o contexto navegable mantenido.
~~~

Resuelve los resultados según su causa:

| Resultado | Respuesta |
|---|---|
| El código viola una frontera autorizada existente | Corrige el código. |
| Una declaración está obsoleta frente a una decisión autorizada posterior | Actualiza declaración y artefactos semánticos relacionados. |
| La frontera nueva es intencionada pero carece de decisión | Ejecuta el prompt de contexto en modo `RECORD_DECISION`; mantén honesta la autoridad y no debilites `CHG001`. |
| El adaptador no observa evidencia necesaria | Mantén incertidumbre visible e invoca la creación del adaptador. |
| La verdad semántica no puede probarse mecánicamente | Devuelve `REVIEW_REQUIRED` y sigue la autoridad declarada. |
| Una desviación temporal necesaria está autorizada | Ejecuta `aak guide waiver-authoring-prompt`; registra una licencia acotada y nunca la conviertas en PASS. |

Repite hasta que pasen los checks o quede una decisión genuina de autoridad o
producto. Un validator verde no compensa tests ausentes ni semántica fabricada.

## 10. Informe final friendly

Informa primero en lenguaje de producto:

~~~text
Resultado de producto entregado:
Dónde pertenece el comportamiento y por qué:
Clasificación: <ROUTINE|FEATURE|MODULE|HOST|BUILD_UNIT|DEPENDENCY|OTHER>
Decisiones requeridas al usuario: <NONE|SUMMARY>
Código y tests modificados:
Artefactos arquitectónicos modificados: <NONE|PLAIN_LANGUAGE_SUMMARY>
Por qué cambió o no cambió la policy:
Registro de decisión del módulo nuevo, si corresponde:
Dependencias introducidas o rechazadas:
Comandos de validación y resultados:
Findings FAIL, WAIVED o REVIEW_REQUIRED restantes:
Riesgos o seguimiento:
~~~

No obligues al usuario a reconstruir el resultado desde nombres de archivo o
identificadores de reglas. Menciónalos como evidencia después de explicar su
significado de producto. Nunca declares completado si solo existen scaffolding,
policy o documentación pero el resultado solicitado no está implementado y
verificado.
