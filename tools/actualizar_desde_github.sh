#!/bin/bash

# ============================================================
# HATO AI LAB — ACTUALIZAR DESDE GITHUB
# ============================================================
# Uso normal:
#   ./tools/actualizar_desde_github.sh
#
# El script trabaja sin parámetros:
#   • Si estás en main, actualiza main.
#   • Si estás en otra rama, actualiza esa rama.
#   • Si existen ramas remotas diferentes, permite seleccionar
#     una de ellas mediante un menú, sin escribir nombres de rama.
#   • Nunca cambia de rama silenciosamente.
# ============================================================

set -e

REPO_PATH="$(git rev-parse --show-toplevel)"
cd "$REPO_PATH"
CURRENT_BRANCH="$(git branch --show-current)"

clear 2>/dev/null || true

echo
echo "============================================================"
echo "       HATO AI LAB — ACTUALIZAR DESDE GITHUB"
echo "============================================================"
echo
echo "📁 Repositorio:"
echo "   $REPO_PATH"
echo
echo "🌿 Rama actual:"
echo "   ${CURRENT_BRANCH:-'(sin rama)'}"
echo

if [ -z "$CURRENT_BRANCH" ]; then
    echo "❌ Error: el repositorio no tiene una rama activa."
    exit 1
fi

# No continuar si hay trabajo local sin guardar.
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️ TIENES CAMBIOS LOCALES."
    echo
    git status --short
    echo
    echo "❌ No se realizará ninguna actualización ni cambio de rama."
    echo "   Primero guarda o publica esos cambios."
    exit 2
fi

echo "📡 Consultando GitHub..."
git fetch origin

# ------------------------------------------------------------
# Selección de rama SIN parámetros
# ------------------------------------------------------------
TARGET_BRANCH="$CURRENT_BRANCH"

# Si estamos en main, main es la opción normal.
# Si estamos en una rama de trabajo, preguntamos solo cuando
# haya otras ramas remotas disponibles.
mapfile -t REMOTE_BRANCHES < <(
    git for-each-ref --format='%(refname:strip=3)' refs/remotes/origin/ \
    | grep -v '^HEAD$' \
    | sort
)

if [ "$CURRENT_BRANCH" != "main" ]; then
    CANDIDATES=()
    for BRANCH in "${REMOTE_BRANCHES[@]}"; do
        [ "$BRANCH" = "$CURRENT_BRANCH" ] && continue
        CANDIDATES+=("$BRANCH")
    done

    if [ "${#CANDIDATES[@]}" -gt 0 ]; then
        echo "🌿 Estás en una rama de trabajo."
        echo
        echo "Selecciona qué rama quieres dejar activa:"
        echo
        echo "   0) Mantener $CURRENT_BRANCH"
        for i in "${!CANDIDATES[@]}"; do
            printf "   %d) %s\n" "$((i + 1))" "${CANDIDATES[$i]}"
        done
        echo
        read -r -p "👉 Opción [0]: " OPTION
        OPTION="${OPTION:-0}"

        if ! [[ "$OPTION" =~ ^[0-9]+$ ]] || [ "$OPTION" -gt "${#CANDIDATES[@]}" ]; then
            echo "❌ Opción inválida."
            exit 3
        fi

        if [ "$OPTION" -gt 0 ]; then
            TARGET_BRANCH="${CANDIDATES[$((OPTION - 1))]}"
        fi
    fi
fi

echo
echo "🎯 Rama seleccionada:"
echo "   $TARGET_BRANCH"
echo

# ------------------------------------------------------------
# Activar la rama seleccionada
# ------------------------------------------------------------
if [ "$CURRENT_BRANCH" != "$TARGET_BRANCH" ]; then
    echo "🔀 Cambiando de rama: $CURRENT_BRANCH → $TARGET_BRANCH"
    if git show-ref --verify --quiet "refs/heads/$TARGET_BRANCH"; then
        git switch "$TARGET_BRANCH"
    else
        git switch --track -c "$TARGET_BRANCH" "origin/$TARGET_BRANCH"
    fi
fi

ACTIVE_BRANCH="$(git branch --show-current)"
if [ "$ACTIVE_BRANCH" != "$TARGET_BRANCH" ]; then
    echo "❌ Error: no fue posible activar la rama '$TARGET_BRANCH'."
    exit 4
fi

LOCAL="$(git rev-parse "$TARGET_BRANCH")"
REMOTE="$(git rev-parse "origin/$TARGET_BRANCH")"

if [ "$LOCAL" = "$REMOTE" ]; then
    echo
echo "============================================================"
    echo "✅ TU PROYECTO YA ESTÁ ACTUALIZADO"
    echo "============================================================"
    echo
echo "🌿 Rama activa:"
    echo "   $ACTIVE_BRANCH"
    echo
echo "📌 Commit:"
    git log -1 --oneline
    echo
    exit 0
fi

AHEAD=$(git rev-list --count "origin/$TARGET_BRANCH..$TARGET_BRANCH")
BEHIND=$(git rev-list --count "$TARGET_BRANCH..origin/$TARGET_BRANCH")

echo "📊 Estado:"
echo "   Commits locales que GitHub no tiene: $AHEAD"
echo "   Commits de GitHub que local no tiene: $BEHIND"
echo

if [ "$AHEAD" -gt 0 ]; then
    echo "⚠️ Tu máquina tiene commits que todavía no están en GitHub."
    echo "❌ No se realizará un pull automático para evitar sobrescribir trabajo."
    exit 5
fi

if [ "$BEHIND" -gt 0 ]; then
    echo "⬇️ Descargando cambios desde GitHub..."
    git pull --rebase origin "$TARGET_BRANCH"
fi

FINAL_BRANCH="$(git branch --show-current)"
FINAL_COMMIT="$(git rev-parse HEAD)"
REMOTE_FINAL="$(git rev-parse "origin/$TARGET_BRANCH")"

echo
echo "============================================================"
if [ "$FINAL_COMMIT" = "$REMOTE_FINAL" ] && [ "$FINAL_BRANCH" = "$TARGET_BRANCH" ]; then
    echo "✅ ACTUALIZACIÓN COMPLETADA"
else
    echo "⚠️ ACTUALIZACIÓN INCOMPLETA — REVISAR ESTADO"
fi
echo "============================================================"
echo
echo "🌿 Rama activa:"
echo "   $FINAL_BRANCH"
echo
echo "📌 Commit:"
git log -1 --oneline
echo
