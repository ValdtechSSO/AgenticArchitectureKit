# Política lingüística

[English — canonical](../language-policy.md)

El inglés es el idioma canónico del núcleo de decisiones incluido, las guías
operativas para el agente, las referencias de reglas portables, herramientas,
contratos, schemas, identificadores, plantillas y resultados legibles por
máquinas. El manifiesto raíz es un mapa para personas, no una segunda fuente
normativa.

Las traducciones españolas se mantienen bajo `docs/es/` para hacer accesible la
arquitectura, pero no definen una semántica independiente. Si una traducción
entra en conflicto con su fuente inglesa, prevalece la fuente inglesa.

Los cambios en `README.md`, `MANIFESTO.md`, `docs/team-guide.md`,
`docs/create-project-from-zero.md`, `docs/capabilities.md` o
`docs/github-governance.md` deben actualizar su traducción española en el
mismo cambio. Si no es posible actualizar una traducción de forma atómica, debe
marcarse como desactualizada al comienzo; queda prohibida la divergencia
silenciosa.

Las guías empaquetadas de bootstrap y gobernanza GitHub bajo
`src/agentic_architecture_kit/data/guides/` son las copias operativas versionadas
que expone la CLI. Sus versiones web bajo `docs/` deben conservar el mismo
procedimiento y solo pueden añadir navegación o contexto específico de la web.

Los identificadores de código y las claves de configuración permanecen en
inglés en todos los idiomas para que los ejemplos sean directamente ejecutables
y localizables.
