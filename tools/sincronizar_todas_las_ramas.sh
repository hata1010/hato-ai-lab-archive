#!/bin/bash

# ============================================================
# HATO AI LAB — SINCRONIZAR TODAS LAS RAMAS LOCALES
# ============================================================
# Uso:
#   ./tools/sincronizar_todas_las_ramas.sh
#
# Propósito:
#   Actualizar las ramas locales desde origin sin cambiar de rama
#   silenciosamente y sin sobrescribir trabajo local.
#
# Reglas de seguridad:
#   • No hace reset --hard.
#   • No hace stash.
#   • No cambia de rama.
#   • Solo actualiza una rama si GitHub es un avance directo.
#   • Si una rama tiene commits propios o está divergida, la deja intacta.
#   • No crea automáticamente ramas locales nuevas.
#   • No toca el actualizador existente.
# ============================================================

set -u

REPO_PATH="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "❌ No estás dentro de un repositorio Git."
    exit 1
}

cd "$REPO_PATH"
CURRENT_BRANCH="$(git branch --show-current)"

if [ -z "$CURRENT_BRANCH" ]; then
    echo "❌ El repositorio no tiene una rama activa."
    exit 1
fi

echo
echo "============================================================"
echo "   HATO AI LAB — SINCRONIZAR TODAS LAS RAMAS LOCALES"
echo "============================================================"
echo
echo "📁 Repositorio:"
echo "   $REPO_PATH"
echo
echo "🌿 Rama actual:"
echo "   $CURRENT_BRANCH"
echo

# La rama actual no puede tener trabajo sin guardar: su actualización
# modificaría el árbol de trabajo.
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️ TIENES CAMBIOS LOCALES EN LA RAMA ACTUAL."
    git status --short
    echo
    echo "❌ No se actualizará ninguna rama."
    echo "   Guarda o publica primero los cambios de la rama actual."
    exit 2
fi

echo "📡 Consultando GitHub..."
if ! git fetch origin --prune; then
    echo "❌ No fue posible actualizar las referencias de origin."
    exit 3
fi

echo
echo "📊 Analizando ramas locales..."

echo

UPDATED=0
CURRENT_UPDATED=0
SKIPPED_AHEAD=0
SKIPPED_DIVERGED=0
SKIPPED_NO_REMOTE=0

# Ramas que están activas en worktrees distintos no se modifican.
while IFS= read -r BRANCH; do
    [ -z "$BRANCH" ] && continue

    REMOTE_REF="refs/remotes/origin/$BRANCH"

    if ! git show-ref --verify --quiet "$REMOTE_REF"; then
        echo "⚪ $BRANCH"
        echo "   Sin rama equivalente en origin — se conserva intacta."
        echo
        SKIPPED_NO_REMOTE=$((SKIPPED_NO_REMOTE + 1))
        continue
    fi

    LOCAL_SHA="$(git rev-parse "refs/heads/$BRANCH")"
    REMOTE_SHA="$(git rev-parse "$REMOTE_REF")"

    if [ "$LOCAL_SHA" = "$REMOTE_SHA" ]; then
        echo "✅ $BRANCH — ya actualizada."
        echo
        continue
    fi

    if git merge-base --is-ancestor "$REMOTE_SHA" "$LOCAL_SHA"; then
        echo "⚠️ $BRANCH — tiene commits locales que GitHub no tiene."
        echo "   No se toca."
        echo
        SKIPPED_AHEAD=$((SKIPPED_AHEAD + 1))
        continue
    fi

    if ! git merge-base --is-ancestor "$LOCAL_SHA" "$REMOTE_SHA"; then
        echo "⚠️ $BRANCH — está divergida respecto a origin."
        echo "   No se toca."
        echo
        SKIPPED_DIVERGED=$((SKIPPED_DIVERGED + 1))
        continue
    fi

    # La rama actual debe avanzar mediante merge --ff-only para actualizar
    # también el árbol de trabajo. Las demás ramas pueden avanzar su ref
    # directamente porque no están activas en el árbol actual.
    if [ "$BRANCH" = "$CURRENT_BRANCH" ]; then
        echo "⬇️ $BRANCH — actualización fast-forward desde GitHub..."
        if git merge --ff-only "origin/$BRANCH"; then
            UPDATED=$((UPDATED + 1))
            CURRENT_UPDATED=1
        else
            echo "   ❌ No se pudo actualizar; se conserva el estado anterior."
            exit 4
        fi
    else
        # No mover una rama que esté activa en otro worktree.
        if git worktree list --porcelain | grep -q "^branch refs/heads/$BRANCH$"; then
            echo "⚠️ $BRANCH — está activa en otro worktree."
            echo "   No se toca."
            echo
            SKIPPED_DIVERGED=$((SKIPPED_DIVERGED + 1))
            continue
        fi

        echo "⬇️ $BRANCH — fast-forward desde GitHub..."
        if git update-ref "refs/heads/$BRANCH" "$REMOTE_SHA" "$LOCAL_SHA"; then
            UPDATED=$((UPDATED + 1))
        else
            echo "   ❌ No se pudo actualizar."
        fi
    fi

    echo
done < <(git for-each-ref --format='%(refname:strip=2)' refs/heads/ | sort)

echo "============================================================"
echo "                  RESULTADO DE SINCRONIZACIÓN"
echo "============================================================"
echo
echo "🌿 Rama actual:              $CURRENT_BRANCH"
echo "⬇️ Ramas actualizadas:       $UPDATED"
echo "⚠️ Ramas con commits locales: $SKIPPED_AHEAD"
echo "⚠️ Ramas divergidas/activas:  $SKIPPED_DIVERGED"
echo "⚪ Sin rama remota:           $SKIPPED_NO_REMOTE"
echo

echo "🌐 Ramas remotas sin rama local:"
REMOTE_ONLY=0
while IFS= read -r REMOTE_BRANCH; do
    [ -z "$REMOTE_BRANCH" ] && continue
    if ! git show-ref --verify --quiet "refs/heads/$REMOTE_BRANCH"; then
        echo "   • $REMOTE_BRANCH"
        REMOTE_ONLY=$((REMOTE_ONLY + 1))
    fi
done < <(git for-each-ref --format='%(refname:strip=3)' refs/remotes/origin/ | grep -v '^HEAD$' | sort)

if [ "$REMOTE_ONLY" -eq 0 ]; then
    echo "   Ninguna."
fi

echo
echo "============================================================"
echo "✅ SINCRONIZACIÓN SEGURA TERMINADA"
echo "============================================================"
echo
echo "📌 Regla aplicada: ninguna rama con trabajo propio fue sobrescrita."
echo

exit 0
