# Implementar AAK en un pipeline de entrega

[English — canonical](../pipeline.md)

Esta es la versión web en español de la guía correspondiente a
`aak guide pipeline`. Conecta Agentic Architecture Kit con integración continua
desde el checkout hasta la protección efectiva del merge.

## 1. Resultado requerido

El pipeline debe ejecutar las versiones exactas del kit y sus extensiones,
observar el código candidato, evaluar los gates portables y propios, conservar
evidencia ligada a la revisión tanto si pasa como si falla y exponer un check
obligatorio que pueda bloquear realmente la entrega.

CI no decide la arquitectura. Demuestra que decisiones declaradas, código
observado, excepciones aceptadas, evidencia de review y revisión actual
coinciden.

## 2. Modelo de ejecución

El comando central es:

```bash
aak validate --base-ref BASE_REVISION --fail-on-review --task-id architecture-ci
```

Su flujo interno es:

```text
toolchain y catálogo
→ policy, waivers, reviews y authorities
→ policy base de confianza
→ adapters.observe(policy["adapter"], root, policy)
→ ObservedArchitecture
→ contratos de módulo y 18 reglas portables
→ resultado ligado a la revisión y código de salida
```

El adaptador solo devuelve hechos. Las reglas, waivers y revisiones semánticas
deciden su resultado arquitectónico.

## 3. Prerrequisitos

El repositorio necesita `.agentic/toolchain.json` válido, policy de arquitectura,
waivers, reviews, authorities, routing CODEOWNERS real, el adaptador seleccionado
instalable y comandos estables para sus reglas arquitectónicas propias. Ejecuta
primero `aak core`, `aak guide bootstrap` y `aak guide github-governance`.

## 4. Ruta rápida: deja que la adopción conecte GitHub Actions

Previsualiza sin escribir y después aplica:

```bash
aak adopt --root . --codeowner @tu-org/architecture --ci github --dry-run
aak adopt --root . --codeowner @tu-org/architecture --ci github
```

La adopción añade el workflow incluido solo si no sobrescribe un CI existente.
En caso contrario informa del trabajo de integración. Para un repositorio nuevo,
inicializa la arquitectura mínima veraz y obtén el workflow con:

```bash
aak template github-architecture.yml
```

## 5. Workflow de referencia para GitHub Actions

La plantilla fijada hace checkout completo, instala AAK, selecciona una base de
confianza, valida y siempre sube la evidencia:

```yaml
name: Architecture conformance

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0
      - uses: actions/setup-python@v7
        with:
          python-version: "3.11"
      - name: Install pinned architecture kit
        run: python3 -m pip install --no-deps agentic-architecture-kit==0.5.0
      - name: Validate architecture
        env:
          BASE_REVISION: ${{ github.event_name == 'pull_request' && github.event.pull_request.base.sha || github.event.before }}
        run: |
          if [ -n "$BASE_REVISION" ] && git cat-file -e "$BASE_REVISION:.agentic/policies/architecture/project-policy.json"; then
            aak validate --base-ref "$BASE_REVISION" --fail-on-review --task-id architecture-ci
          else
            aak validate --fail-on-review --task-id architecture-ci
          fi
      - name: Retain architecture evidence
        if: always()
        uses: actions/upload-artifact@v7
        with:
          name: architecture-evidence-${{ github.run_id }}
          path: .agentic/runtime/evidence/
          if-no-files-found: error
```

Actualiza el pin del workflow y `toolchain.json` atómicamente durante un upgrade
explícito del kit. Usa como punto de partida las versiones de actions emitidas
por la plantilla fijada, no un ejemplo web antiguo copiado a ciegas.

## 6. Por qué existe cada elemento del workflow

| Elemento | Garantía |
|---|---|
| Historial Git completo | La revisión base y los commits antecesores revisados son alcanzables. |
| Pins exactos del kit y extensiones | Reglas, schemas, CLI y observación no derivan silenciosamente. |
| SHA base propio del evento | `CHG001` ve el delta real de policy. |
| `--fail-on-review` | La incertidumbre semántica pendiente no puede aparentar verde. |
| `--task-id` | Se conservan el JSON y manifest de evidencia de la revisión. |
| `if: always()` | Los fallos también conservan sus diagnósticos. |
| Check obligatorio | Un informe fallido bloquea realmente la entrega. |

## 7. Seleccionar la revisión base

En pull requests usa el SHA base del PR; en pushes usa el SHA anterior del
evento. No supongas que todos los eventos apuntan a `origin/main`. Durante la
primera adopción, la base puede no contener policy AAK: comprueba el archivo y
omite `--base-ref` solo en ese bootstrap. Los cambios gobernados posteriores
deben usar validación comparativa.

## 8. Adaptadores incluidos, externos y locales

Los adaptadores `dotnet` y `python` vienen incluidos. Un adaptador externo debe
instalarse junto a AAK y fijarse en `toolchain.json`:

```bash
python3 -m pip install --no-deps \
  agentic-architecture-kit==0.5.0 \
  aak-rust-adapter==1.2.3
```

El proyecto selecciona el nombre del entry point en `project-policy.json`. Un
adaptador `LOCAL_UNCOMMITTED` funciona en su máquina local, pero CI debe fallar
de forma cerrada hasta que esa distribución exacta esté disponible mediante un
canal autorizado privado o público. Nunca comitees un path local absoluto ni
hagas fallback silencioso a otro adaptador.

## 9. Códigos de salida y política del gate

| Salida | Significado |
|---|---|
| `0` | La validación satisface la rigurosidad seleccionada. |
| `1` | Falló una regla o el modo estricto encontró `REVIEW_REQUIRED` pendiente. |
| `2` | Configuración, schema, pin, path o contrato del adaptador inválido. |

`WAIVED` y `REVIEWED` siguen siendo estados aceptados visibles, no `PASS`
mecánico. Una autorización caducada o stale no se aplica.

## 10. Evidencia y artefactos

`--task-id architecture-ci` escribe:

```text
.agentic/runtime/evidence/architecture-ci/{revision}/
  architecture.json
  manifest.json
```

El resultado registra revisión, base, adaptador, findings, evidencia y digests
canónicos de toolchain, policy, waivers, reviews, authorities, catálogo y
arquitectura observada. Súbelo con una retención acorde al riesgo. Regenera la
evidencia runtime; no la mantengas manualmente en Git.

La evidencia de validación arquitectónica es distinta de un checkpoint de
ejecución larga. Cuando una tarea atraviese contextos o runners, usa
`aak guide long-running-execution` y conserva `.agentic/runtime/checkpoints/`
por separado con controles de acceso adecuados para su contenido de
razonamiento y riesgo.

## 11. Reglas arquitectónicas propias del proyecto

AAK evalúa las 18 reglas portables. Una regla del proyecto necesita analyzer,
test arquitectónico, comprobación del compilador o linter conectado por
separado. Créala mediante `aak guide project-rule-authoring-prompt` y ejecuta su
comando estable en el mismo job o en otro obligatorio, por ejemplo:

```yaml
- name: Project architecture rules
  run: dotnet test tests/Architecture/Architecture.Tests.csproj
```

No presentes un analyzer local como resultado portable de AAK.

## 12. Protección de rama y autoridad de review

Exige el check exacto `Architecture conformance / validate` en la rama
protegida. Aplica el modo de `authorities.json`: `team` requiere aprobación
independiente de CODEOWNER; `solo-maintainer` exige el check, prohíbe pushes
directos y usa una atestación externa durable para juicios semánticos. Consulta
`aak guide github-governance` para la configuración completa de plataforma.

## 13. Otras plataformas CI

En otra plataforma conserva el mismo contrato: checkout completo, instalaciones
exactas, cálculo de base de confianza, checks propios, validación AAK estricta,
subida incondicional de evidencia y gate obligatorio de merge o despliegue. El
YAML cambia; inputs, adaptador, códigos de salida y evidencia AAK no.

## 14. Diagnóstico de fallos

1. Para salida 2, comprueba pins, extensiones instaladas, schemas, paths y
   unicidad del entry point.
2. Para `FAIL`, ejecuta `aak explain RULE_ID` y corrige código o una declaración
   inexacta.
3. Para `REVIEW_REQUIRED`, resuelve el juicio bajo la autoridad declarada; no
   fabriques certeza dentro del adaptador.
4. Para waivers o reviews stale, reevalúa fingerprint y digest actuales.
5. Si falta la base, comprueba historial completo y selección de SHA por evento.
6. Si falta el artefacto, comprueba `--task-id` y la subida incondicional.

Nunca amplíes la policy, sustituyas el adaptador, desactives el modo estricto ni
añadas un waiver solo para recuperar el verde.

## 15. Lista de comprobación final

- Se instalan los pins exactos del kit y extensiones.
- El adaptador seleccionado está disponible sin fallback.
- PR, push y bootstrap tratan correctamente sus revisiones base.
- Se ejecutan la validación portable y los checks propios.
- La evidencia se sube al pasar y al fallar.
- La protección de rama exige el nombre exacto del check.
- Los controles de plataforma coinciden con `authorities.json` y CODEOWNERS.
- Una mutación inválida deliberada hace fallar el pipeline.
- Un candidato válido produce evidencia para su commit exacto.

El pipeline solo está completo cuando un check fallido impide realmente la
entrega; el archivo de workflow por sí solo no es enforcement.
