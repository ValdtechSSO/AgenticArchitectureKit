# Aplicación de autoridad en GitHub

Esta es la versión web de la guía versionada que imprime
`aak guide github-governance`.

El validador local puede demostrar que la autoridad está declarada de forma
coherente, que una revisión identifica un principal permitido por `CODEOWNERS` y
que `reviewedAtRevision` es un commit ancestro alcanzable. No puede demostrar
que GitHub haya registrado realmente una aprobación o atestación del mantenedor,
ni que haya activado la protección de rama. Esos son hechos de la plataforma.

Configura `enforcement.mode` según el ownership real del repositorio. La ausencia
del campo equivale a `team` por compatibilidad con versiones anteriores.

## Modo de equipo

Para `team`, configura cada rama indicada en
`.agentic/policies/architecture/authorities.json` con:

- exigir pull request antes de fusionar;
- exigir al menos una aprobación;
- exigir revisión de Code Owners;
- descartar aprobaciones obsoletas cuando se añadan commits;
- exigir el check `Architecture conformance / validate`;
- impedir bypass y pushes directos, también para administradores salvo excepción
  aceptada explícitamente por el equipo.

En la práctica, el modo de equipo exige al menos dos personas: quien abre el
pull request no puede aportar su propia aprobación independiente. Sus reviews
usan `github-pr-review:<URL-o-id-de-review>`.

## Modo de mantenedor individual

Usa `solo-maintainer` únicamente cuando una sola persona es propietaria del
repositorio. El validador exige exactamente un principal único y rechaza los
requisitos de equipo `code-owner-review` y `dismiss-stale-reviews`, que ese
principal no podría satisfacer de forma independiente.

Configura cada rama protegida para:

- exigir que los cambios lleguen mediante pull request;
- exigir el status check de arquitectura;
- impedir pushes directos y forzados;
- no afirmar que existe aprobación independiente o de CODEOWNER.

El mantenedor acepta un juicio semántico publicando fuera del diff candidato un
registro durable en una issue, discusión o workflow aprobado manualmente de
GitHub. Debe contener ID de regla, scope, digest, huella, SHA revisado y decisión.
`approvalEvidence` usa entonces:

```text
github-maintainer-attestation:https://github.com/OWNER/REPOSITORY/issues/NUMBER#issuecomment-ID
```

El agente puede preparar el texto, pero no publicar ni inventar la aprobación
del mantenedor. El modo individual reconoce que existe menos independencia; su
valor es una decisión humana durable y una auditoría honesta, no una auto-review
ficticia.

Cada `protectedScope` de `authorities.json` debe tener un patrón real que lo cubra
en `.github/CODEOWNERS` y pertenezca a todos los principals de esa autoridad. Un
patrón más estrecho dentro del scope no puede retirar esos principals. Para el
scope raíz (`.`), usa una entrada global como `* @equipo/arquitectura`; así se
protegen también `.github/workflows/` y el propio `CODEOWNERS`. Sustituye el
principal incluido cuando cambie el owner o el equipo responsable.

## Flujo de revisión de equipo

1. Crea un commit con el sujeto que requiere revisión semántica.
2. Obtén la aprobación CODEOWNER requerida mediante pull request.
3. Registra la huella exacta y el `ruleDigest` emitidos por el validador.
4. Usa como `reviewedAtRevision` el SHA completo de 40 caracteres que contiene el
   sujeto revisado.
5. Usa en `reviewedBy` el principal CODEOWNER que aprobó y en
   `approvalEvidence` el valor `github-pr-review:<URL-o-id-de-review>`.
6. Añade el registro en un commit posterior y repite la validación estricta.

La alcanzabilidad y la huella impiden reutilizaciones accidentales. CODEOWNERS y
la protección de rama impiden que un agente acepte su propia revisión. El JSON
por sí solo no demuestra aprobación humana.

## Flujo de revisión del mantenedor individual

1. Confirma el sujeto revisado y obtén su SHA completo.
2. Ejecuta la validación o `aak explain` y captura huella y `ruleDigest`.
3. El único principal declarado publica la atestación durable descrita arriba.
4. Genera una plantilla con `--write-review-template`, registra la URL de la
   atestación y conserva ese principal en `reviewedBy`.
5. Confirma `reviews.json`, repite la validación estricta y deja que el status
   check obligatorio proteja el merge.

El validador comprueba el prefijo y la forma de URL de GitHub, pero no consulta
GitHub. Los permisos de plataforma y la separación operativa entre mantenedor y
agente siguen siendo controles externos.

El contrato rechaza un `ruleDigest` ausente. Un digest válido pero modificado
impide aplicar el acuse y produce `REVIEW_REQUIRED`, aunque su huella anterior
todavía pareciera coincidir.

Una revisión solo se comprueba como obsoleta cuando su regla objetivo es
aplicable. Por ejemplo, una revisión de `CHG001` se conserva sin emitir un aviso
de revisión obsoleta durante una autovalidación sin `--base-ref`; la ejecución
comparativa sigue siendo responsable de contrastar su huella exacta.

## Checks en push

El workflow compara los pull requests con su SHA base y los pushes con
`github.event.before`. Un push directo que cambie la policy producirá por tanto
un check fallido, pero únicamente la protección de rama impide que esa mutación
llegue a incorporarse.
