# Publicar la distribución

[English — canonical](../releasing.md)

Una release es un cambio externo que requiere autoridad de mantenedor. Un agente
puede prepararla y verificarla, pero no debe publicarla sin autorización
explícita para esa release.

## Configuración inicial

1. Crea o reserva el proyecto `agentic-architecture-kit` en PyPI.
2. Configura un trusted publisher de PyPI para este repositorio GitHub, workflow
   `publish.yml` y environment `pypi`.
3. Crea el environment protegido `pypi` en GitHub y limita el despliegue a
   mantenedores autorizados y tags de release.
4. Aplica los controles de rama y CODEOWNERS descritos en
   [`github-governance.md`](github-governance.md).

No se guarda ningún token PyPI de larga duración. El job de publicación solicita
una identidad efímera.

## Procedimiento de release

1. Actualiza la versión de forma coherente en `pyproject.toml`, el package, la
   plantilla de toolchain, URLs inmutables de schemas, ejemplos y documentación.
2. Revisa cambios de reglas, schemas, migración y compatibilidad.
3. Ejecuta la suite, autovalidación estricta, build del package y validación del
   wheel aislado contra los ejemplos.
4. Integra mediante la rama protegida con la revisión arquitectónica requerida.
5. Publica una GitHub release cuyo tag sea exactamente `v{versión-del-package}`.
   Crear o subir el tag no inicia por sí solo la publicación; la release de
   GitHub debe pasar al estado publicado.
6. El workflow `Publish Python distribution` comprueba tag y versión, construye,
   verifica y publica mediante trusted publishing de PyPI.
7. Confirma el artefacto y actualiza consumidores mediante un cambio explícito
   de `.agentic/toolchain.json`.

Nunca reutilices una versión publicada ni edites una exportación offline. Un
cambio de regla o schema portable exige nueva versión aunque el formato del
catálogo siga siendo compatible.
