#!/bin/sh
set -e

PKI_DIR="/data/caddy/pki/authorities/local"
NOW="$(date -Iseconds)"

if [ ! -d "$PKI_DIR" ]; then
  echo "$NOW [fix-caddy-pki-perms] PKI dir not found: $PKI_DIR"
  exit 0
fi

CHANGED=0

ensure_mode() {
  path="$1"
  mode="$2"
  if [ -e "$path" ]; then
    current="$(stat -c '%a' "$path" 2>/dev/null || echo '')"
    if [ "$current" != "$mode" ]; then
      chmod "$mode" "$path" 2>/dev/null || true
      echo "$NOW [fix-caddy-pki-perms] chmod $mode $path (was $current)"
      CHANGED=1
    fi
  fi
}

ensure_mode "/data/caddy/pki" 755
ensure_mode "/data/caddy/pki/authorities" 755
ensure_mode "$PKI_DIR" 755
ensure_mode "$PKI_DIR/root.crt" 644

if [ "$CHANGED" -eq 0 ]; then
  echo "$NOW [fix-caddy-pki-perms] permissions already ok, no changes needed"
fi
