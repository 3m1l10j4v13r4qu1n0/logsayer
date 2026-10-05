"""Adaptador para GitHub Copilot: perfiles en `.github/agents/` e
instrucciones por path en `.github/instructions/` (spec §6).

Dos archivos por rol porque Copilot separa las dos cosas: el perfil declara
**quién es** el rol y **qué herramientas** tiene, y la instrucción declara **en
qué rutas** aplica. Con un solo archivo los cuatro prompts llegarían a todos los
contextos del repo y las reglas de la Decidora se aplicarían a los archivos de
la Reverenda Madre.

No se genera `.github/copilot-instructions.md`: Copilot consume `AGENTS.md` de
forma nativa y ese archivo ya es el prompt de proyecto del CLI (D37).

Copilot no declara permisos por ruta. `applyTo` filtra dónde se inyecta la
instrucción, no qué puede escribir el rol, así que el patrón de escritura única
por capa que sostienen opencode y Claude Code queda escrito en la prosa del
template, no en un campo (D38). Los globs de `applyTo` se escriben relativos a
la raíz del repo, que es como los documenta GitHub. Ver HU-17.
"""

from __future__ import annotations

from logsayer.adapters.base import AdapterFile, AdapterSpec

ROLES: tuple[str, ...] = ("mentat", "navigator", "reverend-mother", "truthsayer")

INSTRUCTIONS_DIR = ".github/instructions/logsayer"

copilot_spec = AdapterSpec(
    name="copilot",
    files=(
        tuple(
            AdapterFile(
                f".github/agents/{rol}.agent.md",
                f"adapters/copilot/{rol}.agent.md.j2",
            )
            for rol in ROLES
        )
        + tuple(
            AdapterFile(
                f"{INSTRUCTIONS_DIR}/{rol}.instructions.md",
                f"adapters/copilot/instructions/{rol}.instructions.md.j2",
            )
            for rol in ROLES
        )
    ),
)