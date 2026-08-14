# Aplicación de autoridad en GitHub

El validador local puede demostrar que la autoridad está declarada de forma
coherente, que una revisión identifica un principal permitido por `CODEOWNERS` y
que `reviewedAtRevision` es un commit ancestro alcanzable. No puede demostrar
que GitHub haya registrado realmente la aprobación o activado la protección de
rama. Esos son hechos de la plataforma.

Para repositorios que usen el modelo de autoridad GitHub incluido, configura
cada rama indicada en `.agentic/policies/architecture/authorities.json` con:

- exigir pull request antes de fusionar;
- exigir al menos una aprobación;
- exigir revisión de Code Owners;
- descartar aprobaciones obsoletas cuando se añadan commits;
- exigir el check `Architecture conformance / validate`;
- impedir bypass y pushes directos, también para administradores salvo excepción
  aceptada explícitamente por el equipo.

Los principals de `authorities.json` deben ser usuarios o equipos válidos en
`.github/CODEOWNERS`. Sustituye el principal incluido cuando cambie el owner o el
equipo responsable del repositorio.

## Flujo para registrar una revisión

1. Crea un commit con el sujeto que requiere revisión semántica.
2. Obtén la aprobación CODEOWNER requerida mediante pull request.
3. Registra la huella exacta emitida por el validador.
4. Usa como `reviewedAtRevision` el SHA completo de 40 caracteres que contiene el
   sujeto revisado.
5. Usa en `reviewedBy` el principal CODEOWNER que aprobó y en
   `approvalEvidence` el valor `github-pr-review:<URL-o-id-de-review>`.
6. Añade el registro en un commit posterior y repite la validación estricta.

La alcanzabilidad y la huella impiden reutilizaciones accidentales. CODEOWNERS y
la protección de rama impiden que un agente acepte su propia revisión. El JSON
por sí solo no demuestra aprobación humana.

## Checks en push

El workflow compara los pull requests con su SHA base y los pushes con
`github.event.before`. Un push directo que cambie la policy producirá por tanto
un check fallido, pero únicamente la protección de rama impide que esa mutación
llegue a incorporarse.
