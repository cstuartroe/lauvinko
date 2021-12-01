from django.http import JsonResponse, HttpRequest
from django.shortcuts import render
import json
import mistletoe
from mistletoe.ast_renderer import ASTRenderer

from lauvinko.lang.gloss.gloss import Gloss, InvalidGloss
from lauvinko.lang.lauvinko.morphology import InvalidSyntacticWordSequence
from lauvinko.lang.shared.semantics import Language


def unprocessable_entity(message: str):
    return JsonResponse({"message": message}, status=422)


def react_index(request: HttpRequest):
    return render(request, 'react_index.html')


def page_content(_request: HttpRequest, name):
    with open(f"pages/{name}.md", "r") as fh:
        blob = json.loads(
            mistletoe.markdown(fh, renderer=ASTRenderer)
        )
        return JsonResponse(blob)


def gloss(request: HttpRequest):
    language_code = request.GET.get("language", Language.LAUVINKO.value)

    if language_code not in [l.value for l in Language]:
        return unprocessable_entity(f"Invalid language: {language_code}")

    if "outline" not in request.GET:
        return unprocessable_entity("Must include outline")

    language = Language(language_code)
    outline = request.GET["outline"]

    try:
        gloss = Gloss.parse(outline, language=language)
        return JsonResponse(gloss.as_json())

    except InvalidGloss as e:
        return unprocessable_entity(f"Invalid gloss: {e}")

    except InvalidSyntacticWordSequence as e:
        return unprocessable_entity(f"Invalid syntactic word sequence: {e}")

