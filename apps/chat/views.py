from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import tempfile
from urllib.parse import urlparse
from uuid import uuid4

from core.knowledge.knowledge import ingest_file
from apps.AI.services import agent

FILE_TYPES = {"csv", "pdf", "txt", "text"}
URL_TYPES = {"site", "youtube", "video"}


def normalize_tipo(tipo):
    tipo = (tipo or "").strip().lower()

    if tipo == "video":
        return "youtube"

    return tipo


def is_valid_url(value):
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def source_name_from_url(value):
    parsed = urlparse(value)
    path = parsed.path.strip("/")

    if path:
        return f"{parsed.netloc}/{path}"

    return parsed.netloc


@csrf_exempt
def upload_document(request):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo nao permitido"}, status=405)

    raw_tipo = (request.POST.get("tipo") or "").strip().lower()
    tipo = normalize_tipo(raw_tipo)

    if not tipo:
        return JsonResponse({"error": "Tipo do arquivo nao informado"}, status=400)

    if raw_tipo not in FILE_TYPES and raw_tipo not in URL_TYPES:
        return JsonResponse({"error": "Tipo de conteudo nao suportado"}, status=400)

    document_id = uuid4().hex

    if raw_tipo in URL_TYPES:
        url = (request.POST.get("url") or "").strip()

        if not url:
            return JsonResponse({"error": "URL nao informada"}, status=400)

        if not is_valid_url(url):
            return JsonResponse({"error": "URL invalida"}, status=400)

        try:
            result = ingest_file(
                tipo,
                url,
                filename=source_name_from_url(url),
                document_id=document_id,
            )
        except Exception as exc:
            return JsonResponse({"error": str(exc)}, status=400)

        return JsonResponse({"status": "conteudo processado", **result})

    file = request.FILES.get("file")

    if not file:
        return JsonResponse({"error": "Arquivo nao enviado"}, status=400)

    caminho = None

    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            for chunk in file.chunks():
                tmp.write(chunk)
            caminho = tmp.name

        result = ingest_file(
            tipo,
            caminho,
            filename=file.name,
            document_id=document_id,
        )
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    finally:
        if caminho and os.path.exists(caminho):
            os.unlink(caminho)

    return JsonResponse({"status": "documento processado", **result})


@csrf_exempt
def chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Metodo nao permitido"}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "JSON invalido"}, status=400)

    if not isinstance(body, dict):
        return JsonResponse({"error": "JSON deve ser um objeto"}, status=400)

    pergunta = body.get("message")
    document_id = body.get("document_id")

    if not isinstance(pergunta, str) or not pergunta.strip():
        return JsonResponse({"error": "Mensagem vazia"}, status=400)

    knowledge_filters = None

    if isinstance(document_id, str) and document_id.strip():
        knowledge_filters = {"document_id": document_id.strip()}

    resposta = agent.run(pergunta.strip(), knowledge_filters=knowledge_filters)

    return JsonResponse({"resposta": resposta.content})
