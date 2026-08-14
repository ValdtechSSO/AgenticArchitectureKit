# Manifiesto de arquitectura de repositorio para agentes de programación

[English — canonical](../../MANIFESTO.md) · [Núcleo canónico para el agente](../../src/agentic_architecture_kit/data/norms/agent-core.md) · [Reglas portables](../../src/agentic_architecture_kit/data/norms/portable-rules.md)

> **Estado:** explicación y mapa para personas. Las fuentes normativas
> ejecutables son el núcleo de decisiones y las referencias de reglas incluidas
> en el paquete.

## Propósito

Agentic Architecture Kit permite que un agente cree, modifique y haga evolucionar
un proyecto autónomamente dentro de los límites decididos por el equipo. El
repositorio proporciona contexto, políticas, autoridad y validación suficientes
para saber qué puede cambiar, dónde pertenece el comportamiento y cómo demostrar
la completitud sin pedir a una persona que repita decisiones ya registradas.

La arquitectura no es un árbol exhaustivo. Es el conjunto coherente más pequeño
de capacidades, ownership, contratos, código, validación, navegación y evidencia
justificado por el conocimiento actual.

## Documentación orientada al enforcement

La guía se separa según quién la hace cumplir:

| Responsable | Contenido | Modelo de carga |
|---|---|---|
| Agente | Decisiones caras de deshacer después de implementar | Lectura completa antes de decidir estructura |
| Validador | Restricciones observables cuya reparación es local y reversible | Carga mediante la referencia de un hallazgo |
| Personas | Justificación, adopción y evaluación falsable | Fuera del bootstrap del agente |

La distinción depende del coste de reversión, no del tema. La economía
estructural permanece en el núcleo del agente porque descubrirla tarde puede
obligar a reescribir trabajo. Un nombre de directorio prohibido puede esperar al
validador porque renombrarlo es barato.

La documentación humana no es una puerta trasera para obligaciones sin
enforcement. Reducir una fuente de agente o validador a orientación humana es un
cambio arquitectónico sujeto a decisión y revisión de autoridad.

## Autonomía gobernada

La autonomía es el comportamiento por defecto dentro del producto, ownership,
riesgo y autoridad declarados. Solo se escala una decisión material no delegada:
cambiar el significado del producto, aceptar riesgo, transferir ownership,
debilitar una regla o actuar fuera del alcance autorizado.

El repositorio, no la conversación, conserva la memoria arquitectónica. El
contexto se recupera progresivamente desde un bootstrap determinista mediante
contratos, invariantes, decisiones, dependencias, consumidores, datos, tests y
evidencia ligada a una revisión.

## Modelo de conformidad

Tres capas del proyecto especializan la distribución portable:

1. La policy declara módulos, hosts, proyectos, límites y dependencias.
2. Los waivers registran la aceptación acotada y autorizada de una violación.
3. Las reviews registran un juicio semántico aceptado para un hallazgo exacto.

Las reglas portables no se debilitan silenciosamente mediante la policy. Waivers
y reviews guardan el digest de la semántica bajo la que se concedieron, por lo
que una actualización no reutiliza autoridad antigua contra una regla distinta.

La arquitectura declarada expresa intención; los adaptadores observan código y
artefactos de build. La conformidad compara ambas. Validar sintaxis no basta.

## Bucle operativo

```text
Tarea
  → leer el núcleo preventivo
  → localizar ownership y límites actuales
  → validar antes de modificar un repositorio existente
  → declarar y validar la arquitectura mínima de un repositorio nuevo
  → implementar dentro del límite cohesivo más pequeño
  → seguir referencias normativas solo cuando un hallazgo lo requiera
  → actualizar conjuntamente código, declaración, decisión, enforcement y evidencia
  → volver a validar antes de declarar la tarea completa
  → PASS / FAIL / WAIVED / REVIEWED / NOT_APPLICABLE / REVIEW_REQUIRED
```

Una referencia normativa ausente es un fallo, nunca permiso para reconstruir la
regla de memoria.

## Distribución y ownership del proyecto

La distribución Python versionada contiene validador, schemas, catálogo,
documentos normativos, plantillas neutrales y adaptadores. El consumidor fija la
versión y conserva únicamente policy, autoridades, waivers, reviews, contratos,
decisiones, contexto generado y evidencia.

Vendorizar el validador es una excepción offline explícita.

## Autoridad y evidencia

Los checks deterministas demuestran hechos del repositorio. Los juicios
semánticos permanecen en `REVIEW_REQUIRED` hasta que una revisión autorizada liga
huella, digest de regla, alcance, revisión Git, revisor y evidencia de plataforma.

Las declaraciones y CODEOWNERS son solo la mitad. La protección de rama y las
aprobaciones registradas son hechos de la plataforma.

La completitud procede del build, tests, validación arquitectónica, checks de
riesgo, aprobaciones y evidencia conservada. La afirmación del agente no es
evidencia.

## Evaluación falsable

La arquitectura se evalúa comparando resultados con y sin el kit: colocación,
estructura especulativa, dependencias inválidas, esfuerzo de navegación,
escaladas innecesarias y completitud de evidencia.

La búsqueda semántica, servicios externos de contexto y flujos multiagente son
opcionales y solo se justifican mediante mejora medida.

## Criterio de éxito

El kit tiene éxito cuando un agente nuevo crea la arquitectura mínima, localiza
ownership, recupera contexto suficiente, evoluciona límites sin especulación,
reconoce decisiones fuera de su autoridad, valida su trabajo y entrega el
repositorio a otro agente sin depender de memoria conversacional.

El árbol es una consecuencia. La arquitectura es la relación protegida y
explicable entre decisiones, ownership, código, validación, contexto, autoridad
y evidencia.
