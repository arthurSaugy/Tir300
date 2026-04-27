"""
Helper de stockage Cloudflare R2 (S3-compatible).

Variables d'environnement requises :
    R2_ACCOUNT_ID         identifiant du compte Cloudflare
    R2_ACCESS_KEY_ID      cle d'acces de l'API token R2
    R2_SECRET_ACCESS_KEY  secret de l'API token R2
    R2_BUCKET             nom du bucket (ex: tir300-uploads)
    R2_PUBLIC_URL         URL publique du bucket
                          (ex: https://pub-xxxxxxxx.r2.dev)
"""

from __future__ import annotations

import os
from io import BytesIO

import boto3
from botocore.client import Config


_client = None


def _get_client():
    """Retourne (et met en cache) un client boto3 configure pour R2."""
    global _client
    if _client is None:
        account_id = os.environ['R2_ACCOUNT_ID']
        _client = boto3.client(
            's3',
            endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
            config=Config(signature_version='s3v4'),
            region_name='auto',
        )
    return _client


def _bucket() -> str:
    return os.environ['R2_BUCKET']


def upload_fileobj(fileobj, key: str, content_type: str | None = None) -> None:
    """Uploade un objet binaire (file-like) vers R2 sous la cle donnee."""
    extra = {}
    if content_type:
        extra['ContentType'] = content_type
    _get_client().upload_fileobj(fileobj, _bucket(), key, ExtraArgs=extra)


def upload_bytes(data: bytes, key: str, content_type: str | None = None) -> None:
    """Uploade un blob binaire vers R2 sous la cle donnee."""
    extra = {}
    if content_type:
        extra['ContentType'] = content_type
    _get_client().put_object(Bucket=_bucket(), Key=key, Body=data, **extra)


def delete_object(key: str) -> None:
    """Supprime un objet de R2. Tolere les cles inexistantes."""
    try:
        _get_client().delete_object(Bucket=_bucket(), Key=key)
    except Exception:
        # Si l'objet n'existe pas (deja supprime), on ignore.
        pass


def public_url(key: str) -> str:
    """Construit l'URL publique pour servir un objet depuis le bucket."""
    base = os.environ['R2_PUBLIC_URL'].rstrip('/')
    return f"{base}/{key.lstrip('/')}"


# ---------------------------------------------------------------------------
# Helpers d'image (preview pour la galerie)
# ---------------------------------------------------------------------------

PREVIEW_MAX_SIZE = (800, 800)
PREVIEW_QUALITY = 82


def make_preview(image_bytes: bytes) -> bytes:
    """
    Genere un preview WebP redimensionne a partir d'une image source.
    Conserve le ratio, plus grand cote = PREVIEW_MAX_SIZE max.
    """
    from PIL import Image  # import lazy pour ne pas charger Pillow au boot

    img = Image.open(BytesIO(image_bytes))
    # Convertit en RGB si l'image a un canal alpha incompatible avec webp lossy
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGBA') if img.mode != 'P' else img.convert('RGB')
    img.thumbnail(PREVIEW_MAX_SIZE)
    out = BytesIO()
    img.save(out, format='webp', quality=PREVIEW_QUALITY, method=6)
    return out.getvalue()


def preview_key_for(filename: str, prefix: str = 'galerie') -> str:
    """
    Construit la cle R2 du preview a partir du nom de fichier original.
    Ex: 'photo.jpg' -> 'galerie/photo-preview.webp'
    """
    stem = filename.rsplit('.', 1)[0] if '.' in filename else filename
    return f"{prefix}/{stem}-preview.webp"
