# Prompt para que un agente cree un adaptador tecnológico

[English — canonical](../adapter-authoring-prompt.md)

Usa este prompt para pedir a un agente de programación que cree un adaptador
tecnológico nuevo para Agentic Architecture Kit o amplíe uno existente.
Sustituye todos los valores entre corchetes antes de enviarlo. Este prompt es
guía operativa, no una segunda fuente normativa. El núcleo de decisiones,
catálogo, referencias normativas, esquemas y contrato de adaptadores de la
versión fijada de AAK siguen siendo la autoridad.

## 1. Misión y decisiones proporcionadas

~~~text
Directorio de código del adaptador: <ADAPTER_DIRECTORY>
Nombre de la distribución: <DISTRIBUTION_NAME>
Nombre del entry point: <ADAPTER_NAME>
Lenguaje o ecosistema de código: <LANGUAGE>
Sistema de build o paquetes: <BUILD_SYSTEM>
Versión compatible de AAK: <AAK_VERSION>
Límite de soporte inicial: <SUPPORTED_VERSIONS_AND_CONSTRUCTS>
Rutas generadas, vendor, cache y build: <IGNORED_PATHS>
Composición del repositorio: <SINGLE_TECHNOLOGY|MIXED_TECHNOLOGY|UNKNOWN>
Repositorio de aceptación, si existe: <TARGET_REPOSITORY_OR_NONE>
Aceptación ciega obligatoria: <YES|NO>
Reglas adicionales de organización o proyecto: <EXTENSION_RULES_OR_NONE>

Crea o amplía un adaptador de observación AAK distribuido y versionado por
separado. El adaptador informa de hechos del repositorio; no decide si esos
hechos están permitidos arquitectónicamente.

Trata la semántica de las reglas base de AAK como invariable entre tecnologías.
Traduce únicamente la evidencia que necesitan esas reglas. No introduzcas
conceptos propios de un lenguaje en la semántica portable. No infieras
significado de producto a partir de nombres o paths salvo que la policy del
proyecto declare expresamente esa clasificación.
~~~

La persona que proporciona el prompt es responsable de la garantía, el contrato
para identificar sujetos, las excepciones explícitas y la evidencia aceptable de
cada regla de extensión. El agente implementador es responsable del código,
empaquetado, fixtures, tests positivos y negativos, documentación y evidencia de
verificación.

## 2. Contexto y descubrimiento obligatorios

~~~text
Antes de editar archivos:

1. Ejecuta y lee completamente desde la distribución fijada:

   aak core
   aak guide adapter-development
   aak validate --list-rules

2. Lee el modelo público de observación, el cargador de adaptadores, los schemas
   relevantes y cada referencia normativa requerida por la matriz inferior.
   Nunca reconstruyas de memoria una regla cuya referencia no resuelva.

3. Examina las especificaciones autoritativas del lenguaje y sistema de build.
   Identifica la sintaxis o metadata exacta para unidades de build, identidades
   de source, dependencias, roles de test y output generado. Prefiere manifests
   parseados y árboles sintácticos sobre nombres, convenciones y regex.

   Investiga expresamente el espacio negativo: archivos sin namespace o módulo
   declarado, top-level statements, imports implícitos o globales, aliases,
   compilación condicional, source parcial generado, expresiones dinámicas de
   build, varias unidades de build en un directorio y proyectos de test fuera de
   los roots productivos. Una construcción no está ausente solo porque el parser
   más sencillo no pueda asignarle una identidad.

   Construye un catálogo de paths de output para cada ecosistema soportado. En
   repositorios mixtos, distingue los paths que parsea el adaptador de aquellos
   que solo recorre como evidencia estructural. No declares cobertura completa
   si otro ecosistema necesita su propio adaptador o analyzer.

4. Para un adaptador existente, examina su entry point, fixtures, limitaciones,
   compatibilidad de versión y comportamiento visible antes de proponer cambios.

5. Antes de implementar, produce una matriz de cobertura. Clasifica cada
   capacidad de evidencia como EXACT, HEURISTIC, UNSUPPORTED o CORE_ONLY;
   identifica su fuente y todas las reglas base o extendidas que la consumen.

6. Si se exige aceptación ciega, impide que la fase de implementación acceda al
   repositorio de aceptación, su policy, nombres, layout, historial, índices
   generados o salida de un adaptador de referencia. Usa únicamente contratos
   AAK, especificaciones tecnológicas autoritativas y fixtures sintéticos hasta
   probar y congelar por contenido el candidato. Registra esta frontera en la
   evidencia final.
~~~

No pidas al usuario que diseñe el paquete Python, dataclasses de observación,
helpers de parsing, paths seguros, ordenación, deduplicación o tests. Deriva
esos detalles del contrato AAK fijado. Pregunta solo cuando una respuesta ausente
cambie una garantía, clasificación de sujetos, evidencia aceptada, excepción,
riesgo, ownership o límite de release.

## 3. Separación de responsabilidades

Conserva esta frontera:

~~~text
Adaptador tecnológico
  observa manifests, construcciones de source, identidades, edges, roles y paths

Policy y contratos de módulo
  declaran módulos, hosts, ownership, contratos públicos, dependencias
  permitidas, datos autoritativos, riesgos, invariantes y decisiones

Regla portable o de extensión
  evalúa si los hechos declarados y observados cumplen

Waiver
  acepta una violación acotada sin convertirla en PASS

Revisión semántica
  acepta un fingerprint REVIEW_REQUIRED exacto bajo autoridad declarada
~~~

El adaptador nunca debe ocultar un hecho observado porque pueda existir una
excepción o waiver. Informa del hecho; policy, evaluación de reglas, procesamiento
de waivers o revisión semántica determinan su significado arquitectónico.

Mantén consistentes el recorrido común del repositorio, confinamiento al root,
normalización POSIX, deduplicación, orden determinista y exclusión de output. El
código tecnológico solo debe parsear construcciones que demuestren hechos.

El alcance de observación viene de la policy del proyecto. El adaptador debe
respetar los search roots configurados, pero su informe debe aclarar que no
examinó los archivos exteriores. Un resultado vacío dentro del alcance de la
policy no prueba que el repositorio carezca de archivos coincidentes.

## 4. Contrato de evidencia de las reglas base

Usa esta matriz como contrato inicial obligatorio. La responsabilidad del
adaptador describe la evidencia esperada por el modelo actual de AAK. CORE_ONLY
significa que el adaptador no debe duplicar esa regla en código tecnológico.

| Regla | Garantía invariable | Responsabilidad del adaptador y evidencia fiable | Excepciones e incertidumbre |
|---|---|---|---|
| POL001 | La policy es válida y resuelven las decisiones materiales. | CORE_ONLY: carga, schemas, paths y resolución pertenecen a AAK. | Nunca compensar una policy inválida desde el adaptador. |
| ARC001 | Módulos, hosts, unidades de build, nombres, roles test y ownership declarados y observados coinciden. | Observar roots configurados; descubrir cada unidad de build dentro del alcance y sus nombres desde manifests; obtener roles test de metadata mecánica; parsear identidades; mantener visible el source relevante sin identidad explícita y asociarlo a una unidad solo cuando sea mecánicamente fiable. | Los nombres son heurísticos salvo definición tecnológica. Ownership ausente, implícito o ambiguo permanece visible. Los roots configurados pueden excluir unidades reales y deben declararse como limitación del alcance. |
| MOD001 | Cada módulo observado tiene contrato semántico y router local. | Informar de todos los roots reales bajo el module root configurado. La validación de contrato/router es CORE_ONLY. | Nunca omitir un módulo porque le falte contrato o router. |
| MOD002 | La identidad del contrato coincide con el root del módulo. | Informar de roots reales. La comparación es CORE_ONLY. | Sin excepción tecnológica. |
| MOD003 | Los módulos representan capacidades funcionales, no categorías técnicas configuradas. | Informar de roots sin juzgar si su nombre tiene significado funcional. | La clasificación técnica viene de la policy. |
| FEAT001 | El comportamiento tiene owner de feature cohesivo y sus roots coinciden con policy. | Informar de directorios y source relevantes bajo los feature roots declarados. | Coincidencia física no demuestra cohesión semántica; la incertidumbre requiere revisión. |
| HOST001 | El source del host permanece en adaptación y composición declaradas. | Informar del host root y todo su source relevante, incluyendo paths no permitidos y source sin namespace o módulo explícito. | Nunca filtrar un archivo porque viola un patrón permitido o carece de identidad de source. |
| DEP001 | Los módulos productivos no dependen de hosts. | Informar de edges de build/source, identidades origen/destino, asociación a proyecto y roles test mecánicamente probados. Ejercitar tanto source con namespace/módulo como formas sin identidad, por ejemplo entry points top-level. | Solo tests probados reciben la excepción de consumidor de verificación. Si el modelo público no puede expresar un edge desde source sin identidad, declara el punto ciego o propón un cambio central; nunca omitas el edge. Ownership ambiguo requiere revisión. |
| DEP002 | El acceso entre módulos apunta a un contrato público declarado. | Informar del edge completo con identidad destino suficientemente precisa, incluyendo aliases y formas implícitas dentro del soporte declarado. | El adaptador no decide qué es público. Parsear, marcar heurístico o documentar como no soportados aliases, reflection, wildcards, imports implícitos/globales, carga dinámica, source condicional y código generado. |
| DEP003 | Toda dependencia observada con owner está permitida por policy. | Informar de dependencias locales de build/source soportadas, preservando source, dirección, clase de construcción, confianza y evidencia usada para resolver cada extremo. | Nunca clasificar silenciosamente un edge local como externo ni omitirlo porque un extremo carezca de identidad explícita. |
| OWN001 | Los datos autoritativos tienen exactamente un owner declarado. | Informar solo de evidencia representable por el contrato actual. Si los writes fiables necesitan otro campo, proponer cambio del modelo central. | La falta de analyzer o soporte del modelo requiere revisión. El adaptador no asigna ownership semántico. |
| CHG001 | El crecimiento arquitectónico material y la reducción de enforcement tienen decisión y revisión. | CORE_ONLY: comparación Git y clasificación normativa pertenecen a AAK. | Los nuevos hechos observados no autorizan ampliar policy. |
| STR001 | Se prohíben catch-all y duplicación de inventarios estructurales. | Informar de directorios relevantes excluyendo output generado, vendor, cache y build demostrado. Derivar exclusiones de defaults autoritativos y configuración explícita de cada ecosistema soportado, no solo del lenguaje principal. | Los nombres prohibidos vienen de policy; nunca ocultarlos. En repositorios mixtos, el output desconocido de otro ecosistema sigue visible y se declara como límite de cobertura en vez de adivinarlo. |
| DOC001 | Las referencias normativas y arquitectónicas resuelven con cobertura completa. | CORE_ONLY: referencias y catálogo pertenecen a AAK. | Las referencias ausentes fallan; no inferirlas. |
| WVR001 | Los waivers son explícitos, acotados, autorizados, actuales y ligados a la regla. | CORE_ONLY: informar siempre del hecho subyacente. | Nunca implementar ignores o matching de waivers en el adaptador. |
| AUT001 | La autoridad está declarada y protegida en el repositorio. | CORE_ONLY: authorities y CODEOWNERS pertenecen a AAK. | El enforcement de plataforma sigue siendo evidencia externa. |
| REV001 | Las revisiones ligan finding, digest, scope, autoridad, revisión, reviewer y evidencia exactos. | CORE_ONLY: la validación de reviews pertenece a AAK. | Nunca convertir incertidumbre en PASS dentro del adaptador. |

Para cada fila que no sea CORE_ONLY, mapea la evidencia abstracta a construcciones
tecnológicas autoritativas. Un proyecto MSBuild puede mapearse a unidad de build,
ProjectReference a edge de build, namespace C# a identidad de source y using C#
a dependencia de source. Estos ejemplos no redefinen la semántica portable.

## 5. Contrato de reglas de extensión

Añade un bloque por cada regla de organización o proyecto. No implementes la
regla hasta que todos los campos obligatorios tengan valor explícito.

Para una regla propiedad del proyecto, ejecuta primero
`aak guide project-rule-authoring-prompt`. Esa guía decide si realmente hace
falta ampliar la observación del adaptador y mantiene la semántica de validación
en el evaluator, no en el observador tecnológico.

~~~yaml
ruleId: <STABLE_RULE_ID>
scope: <portable|organization|project>
title: <SHORT_TITLE>
guarantee: <WHAT_MUST_ALWAYS_BE_TRUE>
subjects:
  description: <WHAT_ELEMENTS_THE_RULE_APPLIES_TO>
  identification:
    exact:
      - <AUTHORITATIVE_IDENTIFICATION_SIGNAL>
    heuristic:
      - <OPTIONAL_HEURISTIC_SIGNAL_OR_NONE>
acceptedEvidence:
  - <FACT_REQUIRED_TO_EVALUATE_THE_RULE>
exceptions:
  - condition: <EXPLICIT_EXCEPTION_OR_NONE>
    authority: <WHO_MAY_DECLARE_IT>
observation:
  technologyConstructs:
    - <LANGUAGE_OR_BUILD_CONSTRUCT>
  modelMapping: <EXISTING_MODEL_FIELD_OR_REQUIRED_CORE_CHANGE>
  minimumConfidence: <exact|NAMED_LOWER_CONFIDENCE>
uncertaintyResult: <REVIEW_REQUIRED|NOT_APPLICABLE>
positiveFixtures:
  - <EXAMPLE_THAT_MUST_PASS>
negativeMutations:
  - <ONE_MINIMAL_CHANGE_THAT_MUST_FAIL>
reviewTriggers:
  - <WHEN_EVIDENCE_OR_ACCEPTANCE_BECOMES_STALE>
~~~

Si la evidencia cabe en el modelo público, amplía el adaptador y evaluator según
corresponda. Si no cabe, propón cambios explícitos de modelo, serialización,
schema, índice de contexto, evaluator, catálogo, referencia normativa y
compatibilidad. Nunca sobrecargues un campo ajeno para evitar cambiar el core.

Usa tests arquitectónicos del proyecto o un analyzer nativo para restricciones
locales cuando la portabilidad no aporte beneficio actual. Promueve una regla a
extensión de organización o portable solo cuando su semántica sea estable para
varios consumidores reales.

## 6. Secuencia de implementación

~~~text
1. Registra el límite de soporte y las exclusiones.
2. Construye la matriz regla → evidencia → tecnología.
3. Crea la distribución Python versionada y su entry point único.
4. Implementa observación read-only con paths POSIX confinados al repositorio.
5. Devuelve hechos ordenados y deduplicados con confianza honesta.
6. Crea fixtures sintéticos mínimos; no exijas un producto real ni copies una
   arquitectura de ejemplo como plantilla prescrita.
7. Haz que los fixtures cubran source con identidad explícita y sin ella,
   incluyendo entry points top-level, imports implícitos/globales, aliases,
   tests fuera de roots productivos y varias unidades de build cuando el
   ecosistema lo permita.
8. Añade un fixture positivo y una mutación negativa por cada regla automática
   alimentada por el adaptador.
9. Incluye un edge de source prohibido sin edge de proyecto para demostrar que
   la observación de source realmente se ejecuta. Repítelo con source sin
   identidad o marca esa forma UNSUPPORTED junto a su punto ciego normativo.
10. Incluye paths anidados generados, vendor, cache y build para cada ecosistema
    soportado. En fixtures mixtos, demuestra qué paths permanecen visibles por
    pertenecer a un ecosistema no soportado.
11. Prueba manifests malformados, ambigüedad, escape de paths, output ignorado,
    repetición determinista, search roots solapados, omisiones de alcance y
    construcciones no soportadas.
12. Instala mediante el entry point real y ejecuta el validator fijado contra
    policies completas de fixtures.
13. Documenta cobertura exacta, heurística y no soportada. Nunca presentes una
    colección vacía no soportada o fuera de alcance como prueba de ausencia.
14. Ejecuta tests, chequeos de sintaxis y validación arquitectónica estricta.
15. Si se exige aceptación ciega, congela el candidato antes de inspeccionar el
    objetivo registrando manifest y digest ordenados por contenido. Mantén los
    fixtures escribibles en una copia de test con contenido idéntico; los
    permisos de archivo no demuestran inmutabilidad del código.
~~~

No añadas otro lenguaje, build system, framework o capacidad especulativa sin un
requisito actual y un consumidor de test.

## 7. Tests y evidencia obligatorios

El adaptador terminado debe demostrar:

- su entry point está instalado, es único e invocable y devuelve el modelo
  público exacto de AAK;
- los inputs autoritativos producen las unidades de build, identidades, edges,
  roles y directorios esperados dentro del soporte declarado;
- el source relevante sin namespace o módulo explícito permanece en
  `sourceFiles`; sus dependencias se representan mediante una identidad
  mecánicamente justificada o se declaran como punto ciego explícito del modelo;
- imports implícitos/globales, aliases, construcciones condicionales y source
  generado se parsean, rechazan o declaran no soportados, nunca se omiten por
  accidente;
- output generado, vendor, cache y build se excluyen sin ocultar source normal;
- la exclusión incluye output anidado de cada ecosistema soportado;
- los paths son POSIX, relativos y no pueden escapar del root;
- las referencias de proyecto resuelven a unidades observadas;
- los proyectos de test están cubiertos dentro y fuera de roots productivos
  habituales, y un test demuestra que la policy puede excluirlos expresamente;
- los fixtures multitecnología distinguen la observación tecnológica completa
  del simple recorrido estructural y de los ecosistemas no soportados;
- output y digests son deterministas entre ejecuciones;
- los inputs autoritativos malformados fallan claramente, sin éxito parcial;
- evidencia exacta y heurística tienen confianzas distinguibles;
- cada regla automática soportada tiene una mutación negativa con id y scope
  esperados;
- la evidencia no soportada está documentada y no se representa como una
  colección vacía exacta;
- el toolchain consumidor fija la versión exacta del adaptador.

El contrato actual de AAK no puede expresar explícitamente cobertura completa
frente a observación no soportada. Registra esta limitación en la matriz y el
informe final. La ausencia de findings no demuestra por sí sola cobertura total.

## 8. Protocolo de aceptación ciega

Usa este protocolo cuando exista un repositorio de aceptación y el adaptador
deba generarse sin aprender de él:

~~~text
1. Antes de acceder al objetivo, registra versión candidata, manifest de
   archivos, digest de contenido, resultados de tests, matriz de cobertura y
   construcciones expresamente no soportadas.
2. Congela el candidato. No inspecciones antes la policy, árbol, nombres,
   historial, índices generados ni salida de adaptadores existentes.
3. Tras congelarlo, lee las instrucciones del repositorio y ejecuta el candidato
   en read-only con el alcance real de su policy. No modifiques el objetivo.
4. Reconcilia la observación con un inventario independiente: unidades de build,
   referencias, conteos de source, source sin identidad, proyectos de test,
   directorios relevantes y edges representativos solo presentes en source.
5. Repite con search roots ampliados deliberadamente en memoria o en una policy
   temporal. Así separas puntos ciegos del adaptador y límites de la policy.
6. Si existe adaptador de referencia, compara hechos normalizados solo después
   del freeze. Explica cada diferencia; coincidir aporta evidencia, no un oráculo.
7. Ejecuta el pipeline AAK completo fijado. Si objetivo y candidato fijan
   versiones AAK distintas, usa copias temporales de policy/toolchain y declara
   la diferencia.
8. Clasifica cada discrepancia como ADAPTER_GAP, POLICY_SCOPE_GAP,
   CORE_MODEL_GAP, UNSUPPORTED_ECOSYSTEM o TARGET_CONFORMANCE_FINDING.
9. No parches el candidato congelado durante la aceptación. Una corrección exige
   nueva versión, nuevo digest y una ejecución ciega nueva.
10. Repite la suite sintética desde una copia escribible de contenido idéntico,
    verifica que el digest original no cambió y demuestra que el Git status del
    objetivo no fue alterado por la evaluación.
~~~

Una validación satisfactoria del objetivo demuestra conformidad únicamente para
la cobertura declarada y reconciliada. No elimina los puntos ciegos informados.

## 9. Informe de finalización

Devuelve un informe breve respaldado por evidencia:

~~~text
Distribución y versión del adaptador:
Nombre del entry point:
Límite de lenguaje/build soportado:
Límite de composición del repositorio:
Archivos creados o modificados:
Cobertura de reglas base:
Cobertura de reglas extendidas:
Observaciones exactas:
Observaciones heurísticas:
Observaciones no soportadas y puntos ciegos:
Cambios del contrato central, si existen:
Fixtures positivos:
Mutaciones negativas:
Comandos ejecutados y resultados:
Instalación consumidora y pin de toolchain:
Atestación de frontera ciega y digest anterior al objetivo:
Repositorio de aceptación y alcance de policy:
Reconciliación con inventario independiente:
Comparación con adaptador de referencia, si se usó:
Discrepancias por categoría:
Digest posterior a aceptación y Git status del objetivo:
Riesgos restantes o casos REVIEW_REQUIRED:
~~~

No declares completado el adaptador mientras quede sin resolver un test,
referencia, cambio de modelo o validación estricta obligatorios.
