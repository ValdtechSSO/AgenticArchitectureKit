# Prompt para licencias arquitectónicas

Usa este prompt para indicar a un agente que cree, actualice, revise o elimine
una licencia acotada para una violación concreta de una regla portable de AAK.
El usuario o la autoridad declarada acepta el riesgo arquitectónico; el agente
descubre el hallazgo, deriva los campos exactos, edita el JSON, valida y prueba.

Una licencia registra una decisión excepcional. Nunca demuestra conformidad,
cambia la semántica portable ni convierte un hallazgo en `PASS`.

## 1. Misión y petición mínima del usuario

~~~text
Raíz del repositorio: <DESCUBRIR_EN_EL_WORKSPACE_O_INDICAR>
Modo: <CREATE|UPDATE|REVIEW|REMOVE>
Desviación: <DESCRIPCIÓN_NATURAL_O_HALLAZGO_ACTUAL>
Por qué no puede corregirse ahora: <RESTRICCIÓN_O_UNKNOWN>
Riesgo aceptado: <CONSECUENCIA_CONCRETA_O_UNKNOWN>
Autoridad: <ADR_EXISTENTE_O_RESPONSABLE_DECLARADO_O_UNKNOWN>
Condición de eliminación o revisión: <EVENTO_FECHA_O_UNKNOWN>

Determina si una licencia es el mecanismo correcto. Si lo es, deriva de la
evidencia la regla exacta, su digest actual, el scope mínimo que coincide, un id
estable y el JSON. Pregúntame solo por una aceptación material del riesgo,
decisión de autoridad o condición de eliminación no delegada. Nunca me pidas
escribir JSON, copiar un digest, elegir una ruta ni implementar validación.
~~~

La petición mínima puede ser: «Mantén esta dependencia del host al módulo
durante la migración aprobada por ADR-014 y elimínala cuando exista el contrato
público». El usuario aporta la intención excepcional y la autoridad, no la
serialización.

## 2. Decisión de elegibilidad de la licencia

Clasifica la causa antes de editar `waivers.json`:

| Causa | Respuesta obligatoria |
|---|---|
| Violación accidental de implementación o dependencia | Corregir el código. `NOT_A_WAIVER`. |
| Policy, contrato, ADR, invariante o router obsoleto | Reconciliar la declaración. `NOT_A_WAIVER`. |
| El adaptador no observa evidencia fiable | Ampliar o corregir la observación. `NOT_A_WAIVER`. |
| La verdad semántica no puede demostrarse mecánicamente | Mantener `REVIEW_REQUIRED` y usar la autoridad de review. `NOT_A_WAIVER`. |
| Un nuevo límite intencionado carece de decisión | Registrar y autorizar la decisión; no licenciar el crecimiento normal. `NOT_A_WAIVER`. |
| Una violación conocida de una regla portable no puede eliminarse con seguridad ahora y la autoridad vigente acepta explícitamente el riesgo acotado | `WAIVER_ELIGIBLE`. |

No crees una licencia solo porque la validación esté roja, se acerque un plazo o
el agente pueda editar la gobernanza. Una regla propia del proyecto que no esté
en el catálogo AAK fijado necesita su propio mecanismo de excepciones.

## 3. Límite de autoridad

El agente puede descubrir el hallazgo, proponer el scope mínimo, explicar el
riesgo, redactar la decisión, editar el registro y probarlo. No puede autorizar
su propia propuesta ni inferir aceptación del silencio.

La autorización debe estar delegada por la policy o proceder de la autoridad
humana o de equipo aplicable. Regístrala en una decisión resoluble, normalmente
un ADR. «Haz que la validación pase» no autoriza a aceptar riesgo.

En `UPDATE`, ampliar scope o duración, cambiar riesgo, significado o desviación
exige nueva autorización. Nunca sustituyas automáticamente un `ruleDigest`
obsoleto: `STALE_RULE_DIGEST` obliga a reconsiderar la concesión.

## 4. Contrato de evidencia de las propiedades

| Propiedad | Fuente y regla |
|---|---|
| `version` | Conserva la versión de esquema `1`. |
| `id` | Id estable y único; no lo reutilices para otra decisión. |
| `rule` | Id exacto de la regla portable del hallazgo actual. |
| `ruleDigest` | Digest actual emitido por la versión AAK fijada; nunca de memoria. |
| `scope` | Scope estable más estrecho; todo el repositorio permanece visible para review. |
| `decision` | Desviación específica aceptada, sin afirmar conformidad. |
| `reason` | Restricción actual que impide corregirla; la comodidad no basta. |
| `risk` | Consecuencia arquitectónica, de producto, seguridad, operación o evolución aceptada. |
| `authorizedBy` | Referencias resolubles que demuestran la autoridad aplicable. |
| `expiresOn` | Fecha ISO opcional; no sustituye una condición basada en eventos. |
| `reviewWhen` | Al menos un evento concreto de reconsideración o eliminación. |

Obtén regla, digest, scope, mensaje, evidencia y referencias de la salida JSON
actual o `aak explain <RULE> --format json`. Comprueba que cada `authorizedBy`
resuelva y conserva las licencias no relacionadas.

## 5. Procedimiento por modo

### `CREATE`

Valida y selecciona un único hallazgo elegible. Establece desviación, motivo,
riesgo, autoridad, scope mínimo y condición de eliminación. Añade un registro y
conserva la violación original como `WAIVED`.

### `UPDATE`

Compara registro, hallazgo, digest, decisión, autoridad, scope, caducidad y
condiciones. Aplica solo el delta autorizado. Un digest nuevo o una ampliación
semántica es una nueva decisión de riesgo, no un cambio administrativo.

### `REVIEW`

Comprueba motivo, riesgo, scope mínimo, autoridad, caducidad, digest y
`reviewWhen`. Elige `KEEP`, `REAUTHORIZE`, `NARROW` o `REMOVE`; no edites solo
para reiniciar un plazo.

### `REMOVE`

Confirma que la desviación fue corregida, desapareció o perdió autorización.
Elimina solo el registro obsoleto y exige que el hallazgo sea `PASS`,
`NOT_APPLICABLE`, esté revisado legítimamente o falle visiblemente. Borrar el
registro no corrige código no conforme.

## 6. Reglas de scope y ciclo de vida

Prefiere el scope exacto de proyecto, fuente, dependencia, módulo, host o
artefacto emitido. No uses `.` ni un glob amplio si basta un scope menor.
Demuestra que un caso cercano fuera del scope no queda licenciado.

Revisa o elimina la licencia al caducar, activarse una condición, quedar
obsoleto el digest, perder autoridad, dejar de coincidir el scope, ser seguro
cumplir o cambiar el riesgo. Una licencia sin uso, caducada, amplia, inválida u
obsoleta permanece visible. Nunca licencies el propio hallazgo de gobernanza.

## 7. Secuencia de edición y validación

~~~text
1. Lee instrucciones, core fijado, regla, policy, autoridad, decisiones y licencias.
2. Ejecuta validación JSON y conserva el hallazgo objetivo completo.
3. Aplica la elegibilidad; detén la creación si es NOT_A_WAIVER.
4. Resuelve solo incógnitas materiales de riesgo, autoridad o ciclo de vida.
5. Deriva los campos mecánicos y edita solo el registro objetivo en
   .agentic/policies/architecture/waivers.json.
6. Valida el JSON mediante la validación normal de AAK.
7. Confirma que regla y scope originales devuelven WAIVED, nunca PASS.
8. Confirma que un scope cercano no coincidente sigue sin licencia.
9. Prueba caducidad, digest obsoleto, autoridad ausente y eliminación si cambió
   la herramienta o convención de licencias.
10. Ejecuta validación estricta e informa de todo FAIL, WAIVED y REVIEW_REQUIRED.
~~~

No debilites código, policy, adaptadores, catálogo ni validación para hacer que
aplique la licencia. No inventes un ADR que afirme autorización previa falsa.

## 8. Protocolo de aceptación

El cambio solo está completo cuando:

- el objetivo es una violación actual de una regla portable conocida;
- corregirla ahora es inseguro o inviable por un motivo registrado;
- la autoridad aplicable acepta explícitamente un riesgo concreto;
- cada campo obligatorio tiene evidencia actual;
- el scope es la coincidencia estable mínima y no licencia un caso cercano;
- se autorizó y guardó el `ruleDigest` actual exacto;
- las referencias resuelven y las condiciones son accionables;
- el hallazgo original es `WAIVED`, no `PASS`;
- los estados obsoletos, caducados, sin autoridad o sin uso siguen visibles;
- el informe explica cómo eliminar la desviación.

## 9. Informe final amigable

~~~text
Resultado: <CREATED|UPDATED|KEPT|REAUTHORIZED|NARROWED|REMOVED|NOT_A_WAIVER>
Desviación arquitectónica subyacente:
Por qué una licencia es o no apropiada:
Riesgo aceptado y autoridad:
Regla y scope exactos:
Caducidad y condiciones de revisión/eliminación:
Campos derivados automáticamente:
Validación, incluido el estado WAIVED visible:
Hallazgos FAIL, WAIVED o REVIEW_REQUIRED restantes:
Seguimiento necesario:
~~~

Empieza por la consecuencia arquitectónica, no por el diff del JSON. Si queda
autoridad material sin resolver, mantén visible el fallo y formula una única
pregunta al nivel de decisión.
