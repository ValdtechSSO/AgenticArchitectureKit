# Checkpoints duraderos para ejecuciones largas

[English — canonical](../long-running-execution.md)

Usa este protocolo cuando una tarea pueda durar más que un contexto fiable,
atravesar compactación o handoff, o ejecutarse durante tantas horas que la
memoria conversacional no sea evidencia aceptable. Git conserva el historial;
un checkpoint registra por qué el trabajo está en su estado actual y qué debe
ocurrir después.

## Contrato

Cada checkpoint es inmutable, tiene digest de contenido, se enlaza al anterior
y queda ligado a todas estas entradas:

- el plan original sin cambios, con ruta relativa al repositorio y digest;
- la revisión Git actual y una huella del worktree no ignorado, incluidos
  archivos untracked y modos de archivo;
- el objetivo global y el siguiente objetivo acotado;
- invariantes activos con estado `holds`, `at-risk` o `unknown` y evidencia;
- decisiones acumulativas y su justificación;
- desviaciones acumulativas respecto a referencias exactas del plan;
- riesgos abiertos y resoluciones de riesgo acumulativas;
- evidencia de tests generada por AAK o una razón explícita para no ejecutarlos.

El estado del checkpoint es evidencia de ejecución. Nunca concede permiso
arquitectónico, acepta riesgo, aprueba un ADR, concede un waiver ni sustituye la
policy del proyecto.

## Iniciar y guardar una tarea

Crea el borrador dentro del directorio runtime ignorado de la tarea para que su
edición no cambie la huella del worktree:

```bash
mkdir -p .agentic/runtime/checkpoints/TASK-123
aak template checkpoint-state.json > \
  .agentic/runtime/checkpoints/TASK-123/draft-state.json
```

Completa todos los campos desde evidencia del repositorio y el plan original.
Los arrays son explícitos aunque estén vacíos. No escribas relleno conversacional
como «todo bien». Un invariante incierto usa `unknown`; un riesgo real sigue
abierto. `create` rechaza los placeholders de la plantilla distribuida y el
texto obligatorio vacío.

Ejecuta los tests mediante AAK cuando deba conservarse el resultado:

```bash
aak checkpoint run-test --task-id TASK-123 -- python3 -m unittest discover -s tests -v
```

AAK ejecuta el vector de argumentos sin shell y registra comando, exit code,
timestamps, huellas del workspace anterior y posterior y artefactos stdout y
stderr en streaming con digest y tamaño. No incluyas tokens, contraseñas ni
otros secretos en argumentos o output de tests.

Crea el checkpoint solo cuando el borrador represente el tramo exacto:

```bash
aak checkpoint create \
  --task-id TASK-123 \
  --plan plans/plan-original.md \
  --state .agentic/runtime/checkpoints/TASK-123/draft-state.json
```

Si ningún test es apropiado, declara explícitamente su ausencia:

```bash
aak checkpoint create ... --no-tests-reason "Tramo solo de discovery; no cambió comportamiento ejecutable."
```

Los tests fallidos u obsoletos no impiden crear el checkpoint. Su estado sigue
visible para que otro agente no herede un verde falso.

## Reanudar antes de continuar

No continúes únicamente desde el contexto conversacional. Ejecuta:

```bash
aak checkpoint resume --task-id TASK-123 --plan plans/plan-original.md
```

El comando valida la cadena, el digest del plan original y el workspace exacto;
después emite el plan original completo seguido del último checkpoint completo.
También escribe un recibo de reanudación ligado al contenido. El checkpoint
siguiente y cualquier test registrado por AAK exigen ese recibo.

AAK puede demostrar que el comando suministró esas entradas. No puede demostrar
la cognición privada del modelo ni que una persona comprendiera lo impreso.

Tras reanudar, los cambios normales del worktree producen `IN_PROGRESS` y son
válidos. Los cambios anteriores al recibo producen
`UNRESUMED_WORKSPACE_DRIFT` y fallan de forma cerrada. Si trabajo externo
legítimo modificó el árbol, reconcílialo explícitamente en vez de fabricar un
recibo o reescribir un checkpoint.

## Continuidad del estado

La cadena aplica estas transiciones:

- el objetivo global y la identidad del plan original no cambian en una tarea;
- decisiones y desviaciones son acumulativas y no desaparecen ni se reescriben;
- una decisión sustituida conserva su texto original y nombra su reemplazo;
- eliminar o reescribir un invariante exige una decisión nueva que lo nombre;
- un riesgo abierto no desaparece sin resolución acumulativa y evidencia;
- una evidencia de tests solo puede consumirse en un checkpoint.

Inicia otra cadena cuando cambien realmente el objetivo global o el plan
original. No disfraces un objetivo nuevo como continuación.

## Verificación y retención

Inspecciona el estado o aplícalo como gate:

```bash
aak checkpoint status --task-id TASK-123 --plan plans/plan-original.md
aak checkpoint verify --task-id TASK-123 --plan plans/plan-original.md
```

`verify` informa:

- `CPK001`: schemas, digests, archivos inmutables y enlaces de cadena;
- `CPK002`: estado duradero completo;
- `CPK003`: identidad sin cambios del plan original;
- `CPK004`: recibo de reanudación antes de continuar.

El directorio runtime se ignora por defecto. Consérvalo entre resets de
contexto, máquinas o runners efímeros mediante un artefacto de tarea con acceso
controlado. El JSON puede contener razonamiento de producto, riesgos y nombres
de archivo; aplica la misma retención y confidencialidad que a otra evidencia de
ingeniería.
