"""Validación de CUIT compartida entre modelo y formulario."""

import re

from django.core.exceptions import ValidationError

CUIT_FORMATO = r"^\d{2}-\d{8}-\d$"
MENSAJE_CUIT = "Ingresá el CUIT con formato XX-XXXXXXXX-X (o 11 dígitos sin guiones)."


def normalizar_cuit(valor):
    """Acepta `XX-XXXXXXXX-X` u 11 dígitos y devuelve siempre el formato con guiones."""
    texto = (valor or "").strip().replace(" ", "")
    if texto.isdigit() and len(texto) == 11:
        texto = f"{texto[:2]}-{texto[2:10]}-{texto[10:]}"
    if not re.fullmatch(CUIT_FORMATO, texto):
        raise ValidationError(MENSAJE_CUIT)
    return texto
