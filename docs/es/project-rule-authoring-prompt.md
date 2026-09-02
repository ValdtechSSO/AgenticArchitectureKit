# Prompt para que un agente cree una regla de arquitectura del proyecto

[English — canonical](../project-rule-authoring-prompt.md)

Usa este prompt para pedir a un agente que cree, actualice o reconcilie una regla
de arquitectura aplicable y propiedad de un proyecto, por ejemplo: «todos los
DTO deben ser records». El usuario aporta garantía, identificación de sujetos,
excepciones permitidas y evidencia fiable. El agente completa el diseño,
implementación, tests, documentación, conexión al pipeline y verificación.

Esta guía es operativa, no una segunda fuente normativa. Las reglas del proyecto
amplían sus garantías; no cambian silenciosamente las reglas portables de AAK,
el modelo común de observación ni el significado de `aak validate`.

## 1. Misión y petición mínima del usuario

~~~text
Raíz del repositorio: <DESCUBRIR_DEL_WORKSPACE_O_PROPORCIONAR>
Modo: <CREATE|UPDATE|RECONCILE|PROMOTE_CANDIDATE>
Garantía deseada: <QUÉ_DEBE_SER_SIEMPRE_VERDAD>
Sujetos afectados: <CÓMO_IDENTIFICARLOS_O_UNKNOWN>
Excepciones permitidas: <EXCEPCIONES_EXPLÍCITAS_O_NONE_O_UNKNOWN>
Evidencia fiable: <QUÉ_PRUEBA_CONFORMIDAD_O_INFRACCIÓN_O_UNKNOWN>
Aplicación esperada: <LOCAL_AND_CI|LOCAL_ONLY|ADVISORY_REVIEW>
Fuente de autoridad: <POLICY_ADR_ISSUE_BRIEF_O_UNKNOWN>

Crea la regla fiable más pequeña que aplique la garantía. El usuario define
intención arquitectónica, no código del analyzer, framework de tests,
configuración, paths, identificadores ni comandos de CI. Tú te encargas de
descubrir el repositorio, elegir tecnología, detectar sujetos, crear evaluator,
fixtures, tests negativos, excepciones, documentación, integración, validación
e informe final.

Pregunta solo cuando falte una decisión que cambie materialmente garantía,
sujetos, evidencia aceptada, excepciones, severidad o autoridad. Nunca pidas al
usuario que implemente el observador o evaluator.
~~~

La petición mínima puede ser una frase: «En este proyecto, todo DTO debe ser un
record». Si el repositorio ya declara de forma fiable qué es un DTO, derívalo.
Si hay varias clasificaciones incompatibles, formula una pregunta semántica con
recomendación en vez de adivinar mediante un sufijo.

## 2. Cuatro decisiones y responsabilidades del agente

Cada regla comienza con cuatro decisiones del proyecto:

| Decisión | Pregunta |
|---|---|
| Garantía | ¿Qué debe ser siempre verdad? |
| Identificación de sujetos | ¿Qué elementos exactos están gobernados? |
| Excepciones | ¿Qué casos se permiten y quién puede autorizarlos? |
| Evidencia fiable | ¿Qué observación prueba conformidad, infracción o incertidumbre? |

El agente transforma esas decisiones en id estable, scope, mapeo tecnológico,
evaluator, salida determinista, documentación, fixtures positivos, mutaciones
negativas, tests de falsos positivos y excepciones, comando local y gate de CI.
No inventa semántica para rellenar una decisión ausente.

## 3. Elegir el límite de enforcement correcto

Selecciona el mecanismo más pequeño capaz de probar la garantía:

| Mecanismo | Cuándo usarlo | Ejemplos |
|---|---|---|
| Compilador o analyzer nativo | El lenguaje ofrece sintaxis o símbolos exactos y diagnósticos estables. | Roslyn analyzer, plugin del compilador, regla de linter. |
| Test de arquitectura del proyecto | La fuente, manifests, metadata o modelo compilado permiten evaluación determinista. | Dependencias, annotations, contratos de schema. |
| Check de build/paquete | Un manifest o schema autoritativo aporta evidencia exacta. | Metadata de paquete, despliegue, migraciones. |
| Extensión del adaptador AAK | Una regla existente o evaluator separado necesita más observación tecnológica. | Nueva identidad fuente o forma de dependencia. |
| Extensión del core/catálogo AAK | Hace falta un campo común, evaluator, resultado, schema o referencia y hay valor entre proyectos. | Nueva garantía portable. |
| Review semántico | No existe evidencia mecánica fiable, pero puede vincularse un juicio durable. | Cohesión u ownership. |

Para sintaxis propia del proyecto, prefiere analyzer nativo o test de
arquitectura. El adaptador observa hechos; no debe contener la semántica de
validación. Tampoco sobrecargues un campo de project policy para aparentar que el
validador común aplica la regla.

`aak validate` ejecuta únicamente reglas registradas en el catálogo AAK fijado.
Un analyzer o test del proyecto debe conectarse a sus comandos locales y CI
autoritativos. El informe debe nombrar el comando real y nunca afirmar que un
`PASS` de AAK cubre un check externo.

## 4. Contrato de especificación de la regla

Registra la regla en la convención de arquitectura existente. Si no existe y se
necesita una explicación durable, crea el documento mínimo, por ejemplo
`architecture/rules/<stable-rule-id>.md`; no crees una jerarquía vacía.

Usa este contrato lógico con independencia de la serialización:

~~~yaml
ruleId: <ID_ESTABLE_DE_REGLA_DE_PROYECTO>
scope: project
title: <TÍTULO_CORTO>
guarantee: <OBLIGACIÓN_MUST_O_MUST_NOT_PRECISA>
subjects:
  description: <DESCRIPCIÓN_SEMÁNTICA>
  identification:
    exact:
      - <SEÑAL_AUTORITATIVA>
    heuristic:
      - <SEÑAL_DE_MENOR_CONFIANZA_OPCIONAL>
acceptedEvidence:
  compliant:
    - <PRUEBA_DE_CONFORMIDAD>
  violation:
    - <PRUEBA_DE_INFRACCIÓN>
  uncertainty:
    - <CUÁNDO_LA_EVIDENCIA_ES_INSUFICIENTE>
exceptions:
  - condition: <CONDICIÓN_ESTRECHA_O_NONE>
    authority: <QUIÉN_PUEDE_DECLARARLA>
    evidence: <CÓMO_SE_REGISTRA>
result:
  violation: <FAIL|FALLO_NOMBRADO_DE_LA_HERRAMIENTA>
  uncertainty: <REVIEW_REQUIRED|FAIL_CLOSED|NOT_APPLICABLE>
enforcement:
  mechanism: <ANALYZER|ARCHITECTURE_TEST|BUILD_CHECK|AAK_EXTENSION|REVIEW>
  localCommand: <COMANDO_EXACTO>
  ciGate: <WORKFLOW_O_COMANDO_AGREGADO>
reviewTriggers:
  - <CUÁNDO_REVISAR_REGLA_O_ACEPTACIÓN>
~~~

El formato persistido puede ser Markdown, configuración del analyzer o contrato
de test. No introduzcas un formato máquina nuevo sin un consumidor actual. Une
garantía legible y diagnóstico ejecutable mediante el id estable.

## 5. Reglas de evidencia e incertidumbre

Identificar sujetos de forma fiable es parte de la regla. Prefiere marcadores
semánticos, símbolos del compilador, interfaces, atributos/annotations, roles de
manifest o paths ya establecidos. Nombres y carpetas solo son exactos si el
proyecto los ha hecho autoritativos y el analyzer cubre toda la fuente relevante.

Clasifica la cobertura:

~~~text
EXACT
  parser o modelo semántico autoritativo demuestra el hecho

HEURISTIC
  señal útil con riesgo conocido de falsos positivos o negativos

UNSUPPORTED
  no puede evaluarse un construct relevante

OUT_OF_SCOPE
  exclusión explícita del contrato autorizado de sujetos
~~~

Nunca conviertas `HEURISTIC` o `UNSUPPORTED` en conformidad automática. Usa el
resultado de incertidumbre declarado. Si la herramienta no representa
`REVIEW_REQUIRED`, falla de forma cerrada con un diagnóstico claro.

Código generado, vendor, tests, migraciones, compatibilidad o código externo no
están exentos automáticamente. Cada exclusión necesita contrato y evidencia.

## 6. Modelo de excepciones y autoridad

Una excepción es parte estrecha de la definición o una autorización explícita.
Identifica condición, scope, razón, autoridad, evidencia y trigger de
revisión/caducidad. El evaluator observa el sujeto antes de aplicarla.

No añadas una regla desconocida a `waivers.json`: WVR001 solo admite reglas del
catálogo AAK fijado. Las excepciones de proyecto necesitan un mecanismo propio
soportado por su evaluator. No uses comentarios, nombres de archivo ni globs
amplios como excepciones ocultas.

El agente puede implementar una excepción ya autorizada, pero no concedérsela a
sí mismo porque falle un test negativo.

## 7. Secuencia de implementación y tests

~~~text
1. Lee instrucciones, contexto, policy, contratos, ADR, comandos y gates de CI.
2. Expón las cuatro decisiones y clasifica lo ausente como derivable o material.
3. Inventaría todos los constructs que pueden representar un sujeto, incluidos
   aliases, formas partial/generated, tipos anidados, top-level, múltiples
   unidades de build y áreas multilenguaje aplicables.
4. Elige el enforcement mínimo y explica por qué evidencia más débil no basta.
5. Asigna un id estable sin colisionar con ids portables ni fingir portabilidad.
6. Implementa descubrimiento y evaluación read-only y deterministas con parser
   o API semántica autoritativa cuando exista.
7. Emite diagnóstico con id, sujeto/scope, garantía, evidencia y remediación.
8. Añade fixtures positivos y una mutación negativa aislada por forma prohibida;
   demuestra que falla con este id.
9. Prueba excepciones, entradas inválidas, constructs no soportados, generated y
   vendor, falsos positivos/negativos, repetición y confinamiento de raíz.
10. Ejecuta contra el proyecto y corrige infracciones reales; no debilites regla
    ni amplíes excepciones para poner verde el baseline.
11. Añade el check al agregado local y gate requerido de CI, y demuestra que una
    mutación infractora hace fallar ese gate.
12. Actualiza documento de regla, ADR/invariante y router mediante
    `aak guide architecture-context-authoring-prompt` cuando cambie su significado.
13. Ejecuta tests, suite negativa, `aak validate` y validación estricta. Informa
    por separado los resultados AAK y los de la regla del proyecto.
~~~

La implementación está incompleta si existe el analyzer pero ninguna ruta normal
de desarrollo o CI lo ejecuta.

## 8. Protocolo de aceptación agnóstico al lenguaje

La regla solo se acepta cuando:

- garantía, sujetos, excepciones y evidencia son explícitos y autorizados;
- cada construct gobernado se analiza, declara no soportado o queda fuera de
  scope explícitamente;
- código conforme pasa y cada mutación prohibida falla con id y sujeto exactos;
- los tests de excepción prueban el caso permitido y rechazan uno casi igual;
- evidencia heurística o no soportada nunca produce `PASS` silencioso;
- salida, paths y scopes son deterministas;
- el check se ejecuta por comando local documentado y CI requerido;
- desactivar, borrar o evitar el check es visible en review;
- las infracciones actuales se corrigieron o siguen reportadas;
- la documentación nombra el enforcement real sin atribuirlo al validator AAK;
- un agente nuevo descubre la regla antes de terminar cambios gobernados.

Para «todo DTO debe ser un record», la aceptación prueba cómo se identifica un
DTO y cómo demuestra el lenguaje una declaración record. Revisar solo archivos
`*Dto` es insuficiente salvo que esa convención sea explícitamente autoritativa y
cubra todas las formas de DTO.

## 9. Promoción y evolución

Mantén la regla en el proyecto mientras exprese su política. Considera promoción
organizacional o portable solo cuando varios consumidores reales compartan la
misma garantía agnóstica y contrato de evidencia.

Una promoción que necesite hechos AAK nuevos actualiza explícitamente modelo
común, serialización, contratos de adaptadores, índice de contexto, evaluator,
catálogo, referencia normativa, schemas, compatibilidad y tests de conformidad.
Ejecuta `aak guide adapter-authoring-prompt` para observación tecnológica. No
renombres un test de proyecto como regla AAK sin crear esa ruta completa.

Conserva el id si la garantía sigue siendo compatible. Crea uno nuevo o una
decisión versionada si sujetos, excepciones, evidencia o resultados cambian de
forma incompatible. Reejecuta mutaciones negativas y revisa excepciones.

## 10. Informe final

~~~text
Id y título de regla:
Garantía en lenguaje natural:
Sujetos e identificación exacta:
Excepciones y autoridad:
Evidencia aceptada y clasificación de cobertura:
Mecanismo de enforcement elegido y motivo:
Archivos creados o modificados:
Comando local:
Gate de CI:
Fixtures positivos y mutaciones negativas:
Infracciones actuales y resolución:
Incertidumbre y constructs no soportados:
Cambios de contexto o ADR:
Resultado de validación AAK:
Resultado de la regla del proyecto:
Decisiones solicitadas al usuario, si existen:
Riesgos o triggers restantes:
~~~

No declares finalizada la tarea si la regla depende de heurísticas sin explicar,
ignora constructs, carece de mutación negativa, contiene excepciones no
autorizadas, está fuera del CI normal o se presenta como aplicada por AAK cuando
solo la ejecuta un check externo.
