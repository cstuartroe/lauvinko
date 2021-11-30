from django.http import JsonResponse
from django.shortcuts import render
import json
import mistletoe
from mistletoe.ast_renderer import ASTRenderer


def react_index(request):
    return render(request, 'react_index.html')


def page_content(_request, name):
    with open(f"pages/{name}.md", "r") as fh:
        blob = json.loads(
            mistletoe.markdown(fh, renderer=ASTRenderer)
        )
        return JsonResponse(blob)
