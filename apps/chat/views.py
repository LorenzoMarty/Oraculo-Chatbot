from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import tempfile

from core.knowledge.knowledge import ingest_file
from apps.AI.services import agent


@csrf_exempt
def upload_document(request):
    file = request.FILES.get("file")
    tipo = request.POST.get("tipo")

    if not file:
        return JsonResponse({"error": "Arquivo não enviado"}, status=400)

    # salva temporariamente (funciona sempre)
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        for chunk in file.chunks():
            tmp.write(chunk)
        caminho = tmp.name

    ingest_file(tipo, caminho)

    return JsonResponse({"status": "documento processado"})


@csrf_exempt
def chat(request):
    body = json.loads(request.body)
    pergunta = body.get("message")

    if not pergunta:
        return JsonResponse({"error": "Mensagem vazia"}, status=400)

    resposta = agent.run(pergunta)

    return JsonResponse({"resposta": resposta.content})
