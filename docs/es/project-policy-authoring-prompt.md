# Prompt para que un agente cree la policy del proyecto

[English — canonical](../project-policy-authoring-prompt.md)

Usa este prompt para pedir a un agente de programación que cree, revise,
reconcilie o actualice un `project-policy.json` de AAK. El usuario describe la
intención del producto y los límites materiales en lenguaje natural. El agente
se encarga de la observación, clasificación de evidencias, escritura del JSON,
conformidad con el schema, consistencia entre documentos, validación e informe.

Esta guía es operativa, no una segunda fuente normativa. El core, schema de la
policy, salida del adaptador, contratos, decisiones y referencias de reglas de
la versión exacta fijada siguen siendo la autoridad.

## 1. Misión y petición mínima del usuario

~~~text
Raíz del repositorio: <DESCUBRIR_DEL_WORKSPACE_O_PROPORCIONAR>
Modo: <CREATE_MINIMUM|REVIEW_OBSERVED_PROPOSAL|UPDATE_FOR_CHANGE|RECONCILE_DRIFT>
Resultado de producto o arquitectura solicitado: <INTENCIÓN_EN_LENGUAJE_NATURAL>
Decisiones de límites conocidas: <OPCIONAL_O_UNKNOWN>
Restricciones conocidas: <OPCIONAL_O_UNKNOWN>
Revisión base para comparar: <DESCUBRIR_O_UNKNOWN>

Crea o actualiza la policy de proyecto más pequeña y veraz que permitan la
intención actual, la evidencia del repositorio y las decisiones autorizadas. El
usuario aporta significado, no JSON. Tú te encargas de la observación del
adaptador, mapeo de campos, identificadores, rutas, selectores, formato,
referencias, validación e informe final.

No pidas al usuario que elija propiedades JSON, schemas, sintaxis de rutas,
patrones de namespaces o paquetes, roles de proyecto, sintaxis de selectores de
dependencias ni comandos de validación. Pregunta solo cuando continuar obligaría
a inventar o cambiar materialmente la propiedad de una capacidad, un límite de
host, un límite de compilación/runtime, la dirección de dependencias, la
aplicación normativa, el riesgo aceptado o la autoridad.
~~~

La petición humana mínima útil es una frase, por ejemplo: «Adopta el repositorio
actual sin tratar las carpetas técnicas como módulos de producto» o «Añade la
capacidad de informes aprobada». La raíz, versión fijada, adaptador, modo y policy
actual deben descubrirse del contexto de trabajo siempre que sea posible.

## 2. Qué declara la policy

Mantén separadas estas responsabilidades:

~~~text
Usuario o autoridad de arquitectura delegada
  decide límites de producto, propiedad, dirección de dependencias, aplicación
  normativa y cambios arquitectónicos materiales

Adaptador tecnológico
  observa proyectos, identidades de código, raíces, dependencias y archivos
  fuente específicos de la tecnología

project-policy.json
  declara qué límites observados son intencionados, quién los posee, sus roles,
  la dirección de dependencias permitida y el alcance estructural del proyecto

Contratos de módulo y documentos de dominio
  declaran significado de producto no derivable, propiedad, riesgo e invariantes

Decisiones de arquitectura
  explican y autorizan cambios materiales de límites o dependencias

Validador
  compara la intención declarada con la evidencia observada y las reglas portables
~~~

La policy no es un inventario generado ni un modelo de dominio. Una carpeta,
paquete, namespace, archivo de proyecto o dependencia puede demostrar que existe
una estructura; por sí solo no demuestra que sea intencionada o autorizada.
Nunca copies ciegamente la salida del adaptador a la policy para obtener `PASS`.

## 3. Preparación obligatoria y clases de evidencia

Antes de editar:

~~~text
1. Lee las instrucciones del repositorio y ejecuta el gate de arquitectura.
2. Ejecuta y lee `aak core` desde la versión exacta fijada en toolchain.json.
3. Lee por completo el schema architecture-policy incluido y carga POL001,
   ARC001, MOD001, MOD003, FEAT001, HOST001, DEP001, DEP002, DEP003, CHG001,
   STR001 y DOC001 mediante `aak explain` o las referencias de los findings.
4. Lee policy, toolchain, contratos de módulo, routers locales, system overview,
   documentos de dominio, ADR, waivers y policy base aplicables.
5. Ejecuta el adaptador seleccionado mediante `aak validate --format json` e
   inspecciona toda la evidencia declarada frente a la observada. Trata la salida
   de `aak init` o `aak adopt` como propuesta, nunca como aprobación.
6. Inspecciona manifiestos de build, identidades fuente, aristas de dependencia,
   tests, puntos de ejecución y raíces reales de módulos y hosts.
7. Clasifica cada valor propuesto como AUTHORIZED_DECISION,
   MAINTAINED_DECLARATION, OBSERVED_FACT, INFERENCE, ASSUMPTION o UNKNOWN y
   registra su origen.
8. Compara con la revisión base objetivo cuando ya exista policy, para que los
   permisos nuevos y reducciones de enforcement sigan visibles para CHG001.
~~~

La precedencia depende de la pregunta. El adaptador es autoridad sobre lo que
puede observar mecánicamente. Las decisiones aceptadas y documentos semánticos
mantenidos son autoridad sobre la intención. Si discrepan, clasifica la causa;
no reescribas silenciosamente ninguno.

## 4. Contrato de evidencia de las propiedades

Rellena la policy con esta matriz:

| Propiedad | Qué declara | Evidencia fiable | Atajo prohibido |
|---|---|---|---|
| `$schema`, `version` | Contrato exacto consumido por el kit fijado. | Schema incluido y documento compatible existente. | No copies de memoria una URL o versión más nueva. |
| `project` | Identidad máquina estable del producto. | Policy existente, identidad del producto/paquete o decisión explícita. | No la derives de un directorio temporal o ruta de una máquina. |
| `adapter` | Observador tecnológico del repositorio. | Adaptador fijado e instalado más artefactos soportados. | No elijas el que produzca una salida más permisiva. |
| `adapterConfig` | Configuración de observación específica del adaptador. | Contrato documentado del adaptador y necesidad real. | No pongas aquí reglas portables o decisiones de producto. |
| `roots.modules`, `roots.hosts` | Convenciones de búsqueda de capacidades y hosts. | Layout real o explícitamente autorizado. | No crees arquitectura vacía para imitar una plantilla. |
| `projectSearchRoots` | Lugares donde se observan unidades de build. | Layout de build/paquetes y contrato del adaptador. | No estreches las raíces para ocultar un proyecto. |
| `structureSearchRoots` | Lugares gobernados por controles estructurales. | Alcance actual del código y exclusiones explícitas. | No excluyas un directorio infractor para obtener `PASS`. |
| `moduleContract` | Nombre, schema y campos de inventario prohibidos del contrato. | Valores fijados por AAK o convención compatible explícita. | No debilites campos prohibidos para duplicar estructura generada. |
| `technicalModuleNames` | Nombres que no pueden fingir ser capacidades funcionales. | Valores portables más vocabulario técnico estable del proyecto. | No elimines un nombre porque ya exista un módulo técnico. |
| `forbiddenDirectoryNames` | Nombres catch-all prohibidos en el alcance. | Valores portables más reglas estructurales específicas. | No lo uses para gustos de estilo o nombres transitorios. |
| `modules[].id` | Identidad estable de una capacidad funcional. | Vocabulario autorizado y contrato de módulo coincidente. | No promociones una capa, framework, carpeta o equipo a módulo. |
| `modules[].root` | Raíz real de código propiedad del módulo. | Observación reconciliada con la decisión de capacidad. | Una carpeta sola no justifica un módulo. |
| `modules[].featureRoot`, `featureAreas` | Áreas cohesivas gobernadas de comportamiento. | Comportamiento, vocabulario, estado, invariantes y ciclo de vida actuales. | No conviertas cada handler, endpoint, comando o carpeta en feature raíz. |
| `modules[].namespacePatterns` | Identidades fuente que pertenecen mecánicamente al módulo. | Declaraciones fuente y evidencia soportada por el adaptador. | No las infieras de nombres que el adaptador no considera fiables. |
| `modules[].contractNamespacePatterns` | Identidades que forman un contrato público entre módulos. | Consumidor actual y límite público explícito. | No expongas implementación de forma especulativa. |
| `modules[].decisionRefs` | Decisiones que gobiernan un límite material de módulo. | ADR aceptados y resolubles u otros documentos autorizados. | No inventes referencias ni cites ADR no relacionados. |
| `hosts[].id`, `root` | Identidad y raíz de un límite de ejecución/adaptación. | Necesidad actual de ejecución, entrega, scheduling o composición. | No uses un host para poseer comportamiento de aplicación. |
| `hosts[].allowedSourcePatterns` | Código permitido para adaptar y componer en el host. | Entry points mínimos reales y rutas observadas. | No uses patrones amplios para ocultar comportamiento en el host. |
| `hosts[].namespacePatterns` | Identidades fuente pertenecientes al host. | Declaraciones fuente y evidencia soportada. | No declares identidades ausentes del código. |
| `hosts[].decisionRefs` | Decisiones que gobiernan un límite material de host. | Decisión aceptada y resoluble para la necesidad actual. | No crees hosts para mecanismos de entrega futuros. |
| `projects[].path`, `name` | Unidad exacta de build observada. | Manifiestos soportados y nombres realmente declarados. | No inventes un proyecto para reflejar una carpeta. |
| `projects[].owner` | Módulo o host responsable de la unidad. | Especificidad de raíz, propiedad mantenida y decisión autorizada. | La cercanía o una dependencia no demuestran propiedad. |
| `projects[].role` | Rol arquitectónico que aplica la unidad. | Evidencia de tests, contenido, consumidores y límite decidido. | No etiquetes producción como `test` o `contracts` para debilitar reglas. |
| `projects[].publicContract` | Si una unidad de contratos es destino público permitido. | Consumidor actual entre módulos y decisión explícita. | No marques aplicación interna como pública por conveniencia. |
| `projects[].decisionRefs` | Decisiones que respaldan un límite material de build. | Decisión aceptada que explica el límite aplicado. | No añadas proyectos porque el lenguaje lo permita. |
| `allowedProjectDependencies[]` | Aristas exactas actualmente autorizadas. | Arista observada más propiedad, rol, dirección, consumidor y decisión válidos. | Observar no autoriza; no copies todas las aristas en bloque. |
| `dependencyRules[]` | Permiso escalable para una clase de aristas. | Dirección explícita y decisión que justifique la amplitud del selector. | No sustituyas aristas precisas por selectores amplios para ahorrar mantenimiento. |

Omite propiedades opcionales sin significado actual o evidencia fiable. Usa
arrays vacíos solo cuando «ninguno declarado actualmente» sea verdad, no para
evitar observar arquitectura existente.

## 5. Registro de evidencias de la policy

Antes de editar, genera este registro en el informe de la tarea, no en el JSON:

| Sujeto de policy | Declaración propuesta | Evidencia y clase | Coincidencia observada | Delta base | Requiere decisión |
|---|---|---|---|---|---|
| Alcance global y adaptador | ... | ... | sí/no/desconocido | ninguno/añadir/cambiar | sí/no |
| Cada módulo | ... | ... | sí/no/desconocido | ninguno/añadir/cambiar/eliminar | sí/no |
| Cada host | ... | ... | sí/no/desconocido | ninguno/añadir/cambiar/eliminar | sí/no |
| Cada proyecto y rol | ... | ... | sí/no/desconocido | ninguno/añadir/cambiar/eliminar | sí/no |
| Cada dependencia exacta | ... | ... | sí/no/desconocido | ninguno/añadir/eliminar | sí/no |
| Cada regla de dependencia | ... | ... | sí/no/desconocido | ninguno/añadir/cambiar/eliminar | sí/no |
| Enforcement estructural | ... | ... | sí/no/desconocido | ninguno/aumentar/reducir | sí/no |

Cada fila que otorgue un límite, contrato público, permiso de dependencia o
reducción de enforcement nuevos debe identificar la decisión que lo autoriza.
Los valores mecánicos como rutas se derivan después de establecer la decisión.

## 6. Algoritmo de creación según el modo

### `CREATE_MINIMUM`

Empieza con el adaptador y alcance de búsqueda veraces. Mantén módulos, hosts,
proyectos y permisos vacíos hasta que requisitos actuales y estructura real o
inmediatamente materializada los justifiquen. No copies la policy de ejemplo.

### `REVIEW_OBSERVED_PROPOSAL`

Para cada módulo, host, proyecto, rol, namespace y dependencia propuestos por el
adaptador:

1. confirma que el hecho observado es actual y está bien identificado;
2. decide si representa arquitectura intencionada o drift accidental;
3. verifica propiedad funcional y justificación del límite;
4. consérvalo solo si intención y evidencia coinciden;
5. si no, corrige implementación, clasificación, observación o propuesta en vez
   de legitimar el accidente;
6. crea contratos ausentes mediante su prompt y decisiones o contexto mediante
   `aak guide architecture-context-authoring-prompt`, siempre desde significado
   autorizado.

### `UPDATE_FOR_CHANGE`

Parte de la policy base y realiza el delta mínimo requerido por el cambio
aprobado. Ejecuta `aak guide module-contract-authoring-prompt` si se crean o
cambian semánticas de módulo. Ejecuta
`aak guide architecture-context-authoring-prompt` si deben cambiar decisiones,
invariantes, overview o routers. Añade referencias de decisión antes de depender
de un módulo, host, unidad de build, contrato público, permiso de dependencia o
reducción de enforcement nuevos. Entrega juntos implementación, policy,
contratos, routers, decisiones, tests y contexto.

### `RECONCILE_DRIFT`

Clasifica cada discrepancia antes de editar:

~~~text
IMPLEMENTATION_DRIFT
  devuelve el código y build a la policy ya autorizada

STALE_POLICY
  actualiza la policy desde una decisión autorizada más reciente y su implementación

OBSERVATION_GAP
  ejecuta aak guide adapter-authoring-prompt; no adivines ni ocultes evidencia

UNAUTHORIZED_BOUNDARY
  elimina o rediseña el límite, u obtén una decisión antes de declararlo

INSUFFICIENT_EVIDENCE
  mantén visible la discrepancia y pide solo la decisión material ausente
~~~

Nunca supongas que gana el código por existir ni que gana la policy cuando la
evidencia mantenida demuestra que está obsoleta.

## 7. Gate de intervención del usuario

Continúa autónomamente cuando requisitos, autoridad del repositorio, decisiones
aceptadas, contratos y evidencia del adaptador determinen una policy segura.

Haz una sola pregunta breve en lenguaje natural únicamente si las alternativas
pendientes cambiarían materialmente:

- si un comportamiento forma una capacidad funcional separada;
- qué capacidad posee una unidad de build o contrato público;
- si un mecanismo de ejecución merece un límite de host;
- si se acepta una dirección o permiso escalable de dependencia;
- si la estructura observada es intencionada o debe corregirse;
- si puede reducirse el enforcement normativo;
- quién tiene autoridad para aprobar la decisión arquitectónica.

Recomienda la opción segura más pequeña y explica su consecuencia. Nunca pidas
al usuario editar JSON, elegir campos, construir selectores, normalizar ids o
transcribir la salida del adaptador.

## 8. Bucle de validación y corrección

La policy solo está completa después de:

~~~text
1. Parsearla y validarla con el schema architecture-policy exacto incluido.
2. Ejecutar `aak validate` y resolver POL001 antes de interpretar resultados.
3. Reconciliar por causa todas las discrepancias ARC001.
4. Resolver findings MOD, FEAT, HOST, DEP, STR y DOC aplicables sin ampliar la
   policy únicamente para silenciarlos.
5. Ejecutar `aak validate --base-ref <TARGET_BASE> --fail-on-review` cuando
   exista policy base para que CHG001 evalúe el crecimiento arquitectónico.
6. Ejecutar tests de arquitectura específicos y build/tests afectados.
7. Regenerar `aak context index` cuando cambien límites mantenidos.
8. Comparar el diff final con el registro y rechazar permisos sin explicación,
   hechos observados ausentes, referencias obsoletas y placeholders.
~~~

Un `PASS` del estado actual no autoriza un límite nuevo. Un
`REVIEW_REQUIRED` comparativo sigue visible hasta gestionarlo mediante la
autoridad declarada. Un waiver no aprueba el crecimiento arquitectónico normal.

## 9. Informe final

~~~text
Modo y raíz del repositorio:
Versión AAK, schema y adaptador fijados:
Arquitectura representada en lenguaje natural:
Registro de evidencias de policy:
Entradas de la propuesta observada conservadas y motivo:
Entradas rechazadas y acción correctiva:
Módulos, hosts, proyectos y roles cambiados:
Permisos de dependencia añadidos, eliminados o rechazados:
Enforcement estructural cambiado o conservado:
Referencias de decisión y autoridad:
Contratos, routers, ADR, tests o código relacionados modificados:
Decisiones solicitadas al usuario, si existen:
Comandos y resultados de validación:
Findings FAIL, WAIVED o REVIEW_REQUIRED restantes:
~~~

No declares finalizada la tarea si la policy contiene valores de ejemplo,
placeholders, intención inventada, discrepancias sin explicar, permisos no
autorizados, referencias sin resolver o cambios materiales que solo existen en
la conversación.
