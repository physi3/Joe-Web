from pathlib import Path

from .thmd import Script, ParseTHMC, CompileTHMD

from django.http import HttpResponse

def MancinoScript():
    script_directory = Path(__file__).parent
    source_path = script_directory / "mancino.thmc"
    with source_path.open("rb") as compiled_file:
        return ParseTHMC(compiled_file.read())


def MancinoView(request):
    script_directory = Path(__file__).parent
    template_path = script_directory / "template.html"

    with template_path.open("r", encoding="utf-8") as template_file:
        template = template_file.read()

    script = MancinoScript()
    html = script.HTML(template)
    return HttpResponse(html, content_type="text/html")