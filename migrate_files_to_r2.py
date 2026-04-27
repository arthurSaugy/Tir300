"""
Script one-shot pour migrer les fichiers existants du repo vers Cloudflare R2.

A executer UNE fois en local apres avoir configure les variables R2_* dans .env.

Mappe :
    static/event_images/<f>           -> R2: event_images/<f>
    static/uploads/galerie/<f>        -> R2: galerie/<f>
    static/resultats_pdfs/<f>         -> R2: resultats_pdfs/<f>

Pour les images de la galerie :
    - les originaux sont uploades sous galerie/<filename>
    - les previews -preview.webp sont uploades sous galerie/<stem>-preview.webp
    - si une image n'a pas de preview, on en genere un automatiquement

Usage :
    python migrate_files_to_r2.py            # dry-run, liste ce qui serait fait
    python migrate_files_to_r2.py --apply    # uploade vraiment
    python migrate_files_to_r2.py --apply --skip-existing
                                             # n'uploade que les cles absentes
"""
from __future__ import annotations

import argparse
import mimetypes
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import storage  # noqa: E402  (apres load_dotenv)


ROOT = Path(__file__).resolve().parent
STATIC = ROOT / 'static'

EVENT_DIR = STATIC / 'event_images'
GALERIE_DIR = STATIC / 'uploads' / 'galerie'
RESULTATS_DIR = STATIC / 'resultats_pdfs'

# Fichiers de event_images a NE PAS migrer (assets statiques, pas des uploads).
EVENT_SKIP = {'default_placeholder.jpg'}


def _guess_content_type(path: Path) -> str | None:
    ctype, _ = mimetypes.guess_type(path.name)
    return ctype


def _key_exists(key: str) -> bool:
    """Verifie si une cle existe deja dans R2."""
    try:
        storage._get_client().head_object(Bucket=storage._bucket(), Key=key)
        return True
    except Exception:
        return False


def _upload_file(path: Path, key: str, *, apply: bool, skip_existing: bool) -> str:
    """Uploade un fichier local vers R2. Retourne un libelle pour le log."""
    if skip_existing and _key_exists(key):
        return f"  SKIP (deja present)  {path.name:40s}  ->  {key}"

    if not apply:
        return f"  DRY  {path.name:40s}  ->  {key}"

    ctype = _guess_content_type(path)
    with path.open('rb') as f:
        storage.upload_fileobj(f, key, content_type=ctype)
    return f"  OK   {path.name:40s}  ->  {key}"


def migrate_event_images(*, apply: bool, skip_existing: bool) -> None:
    print("\n=== event_images ===")
    if not EVENT_DIR.is_dir():
        print(f"  (pas de dossier {EVENT_DIR}, skip)")
        return
    for f in sorted(EVENT_DIR.iterdir()):
        if not f.is_file():
            continue
        if f.name in EVENT_SKIP:
            print(f"  --   {f.name}  (skip, asset statique)")
            continue
        key = f"event_images/{f.name}"
        print(_upload_file(f, key, apply=apply, skip_existing=skip_existing))


def migrate_galerie(*, apply: bool, skip_existing: bool) -> None:
    print("\n=== galerie (originaux + previews) ===")
    if not GALERIE_DIR.is_dir():
        print(f"  (pas de dossier {GALERIE_DIR}, skip)")
        return

    files = sorted(p for p in GALERIE_DIR.iterdir() if p.is_file())
    originals = [p for p in files if '-preview.webp' not in p.name]
    previews = {p.name for p in files if '-preview.webp' in p.name}

    for orig in originals:
        # Original
        key = f"galerie/{orig.name}"
        print(_upload_file(orig, key, apply=apply, skip_existing=skip_existing))

        # Preview : si fichier preview deja present sur disque, on le pousse
        # tel quel ; sinon on le genere a la volee depuis l'original.
        stem = orig.stem
        preview_name = f"{stem}-preview.webp"
        preview_key = f"galerie/{preview_name}"

        if preview_name in previews:
            preview_path = GALERIE_DIR / preview_name
            print(_upload_file(preview_path, preview_key, apply=apply, skip_existing=skip_existing))
        else:
            # Genere un preview a la volee
            if skip_existing and _key_exists(preview_key):
                print(f"  SKIP (deja present)  [preview genere]                ->  {preview_key}")
                continue
            if not apply:
                print(f"  DRY  [preview genere de {orig.name:24s}]   ->  {preview_key}")
                continue
            try:
                with orig.open('rb') as f:
                    img_bytes = f.read()
                preview_bytes = storage.make_preview(img_bytes)
                storage.upload_bytes(preview_bytes, preview_key, content_type='image/webp')
                print(f"  OK   [preview genere de {orig.name:24s}]   ->  {preview_key}")
            except Exception as e:
                print(f"  ERR  [preview genere de {orig.name}] : {e}")


def migrate_resultats(*, apply: bool, skip_existing: bool) -> None:
    print("\n=== resultats_pdfs ===")
    if not RESULTATS_DIR.is_dir():
        print(f"  (pas de dossier {RESULTATS_DIR}, skip)")
        return
    for f in sorted(RESULTATS_DIR.iterdir()):
        if not f.is_file():
            continue
        key = f"resultats_pdfs/{f.name}"
        print(_upload_file(f, key, apply=apply, skip_existing=skip_existing))


def _check_env() -> bool:
    needed = ['R2_ACCOUNT_ID', 'R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY', 'R2_BUCKET', 'R2_PUBLIC_URL']
    missing = [v for v in needed if not os.environ.get(v)]
    if missing:
        print("ERREUR : variables d'environnement R2 manquantes :", ', '.join(missing))
        print("Definis-les dans .env (voir .env.example) avant de relancer.")
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Migration des fichiers locaux vers Cloudflare R2.")
    parser.add_argument('--apply', action='store_true', help="Effectue vraiment les uploads (sinon dry-run).")
    parser.add_argument('--skip-existing', action='store_true', help="Ne reuploade pas les cles deja presentes dans R2.")
    args = parser.parse_args()

    if not _check_env():
        return 1

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"=== Migration fichiers -> R2 [{mode}] ===")
    print(f"Bucket : {os.environ['R2_BUCKET']}")
    print(f"Public URL : {os.environ['R2_PUBLIC_URL']}")

    migrate_event_images(apply=args.apply, skip_existing=args.skip_existing)
    migrate_galerie(apply=args.apply, skip_existing=args.skip_existing)
    migrate_resultats(apply=args.apply, skip_existing=args.skip_existing)

    print("\nTermine.")
    if not args.apply:
        print("(Dry-run. Pour uploader vraiment : --apply)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
