import os
import subprocess
import uuid
import shutil
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="LaTeX to PDF API")

# Diretório temporário para processamento
TEMP_DIR = "/tmp/latex_processing"
os.makedirs(TEMP_DIR, exist_ok=True)

class LatexRequest(BaseModel):
    content: str

def cleanup(directory: str):
    """Remove o diretório temporário após o uso."""
    if os.path.exists(directory):
        shutil.rmtree(directory)

@app.post("/compile")
async def compile_latex(request: LatexRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(TEMP_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    tex_file = os.path.join(job_dir, "document.tex")
    pdf_file = os.path.join(job_dir, "document.pdf")
    
    # Salva o conteúdo LaTeX no arquivo
    with open(tex_file, "w") as f:
        f.write(request.content)
    
    try:
        # Executa o pdflatex
        # -interaction=nonstopmode evita que o processo pare em erros
        process = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", job_dir, tex_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if not os.path.exists(pdf_file):
            # Se o PDF não foi gerado, houve um erro no LaTeX
            error_msg = process.stdout if process.stdout else process.stderr
            # cleanup(job_dir) # Removido para evitar conflito com FileResponse imediato
            raise HTTPException(status_code=400, detail=f"Erro na compilação LaTeX: {error_msg}")
        
        # Retorna o arquivo e agenda a limpeza
        response = FileResponse(pdf_file, media_type="application/pdf", filename="document.pdf")
        background_tasks.add_task(cleanup, job_dir)
        return response

    except Exception as e:
        cleanup(job_dir)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    checks = {}

    # Verifica se o pdflatex está disponível
    try:
        proc = subprocess.run(
            ["pdflatex", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        checks["pdflatex"] = proc.returncode == 0
        if not checks["pdflatex"]:
            checks["pdflatex_error"] = (proc.stderr or proc.stdout).strip()
    except Exception as e:
        checks["pdflatex"] = False
        checks["pdflatex_error"] = str(e)

    # Verifica se é possível criar e remover arquivos em TEMP_DIR
    try:
        test_dir = os.path.join(TEMP_DIR, f"healthcheck_{uuid.uuid4().hex}")
        os.makedirs(test_dir, exist_ok=True)
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        os.rmdir(test_dir)
        checks["temp_dir_writable"] = True
    except Exception as e:
        checks["temp_dir_writable"] = False
        checks["temp_dir_error"] = str(e)

    healthy = checks.get("pdflatex") and checks.get("temp_dir_writable")
    result = {"status": "healthy" if healthy else "unhealthy", "checks": checks}
    if healthy:
        return result
    raise HTTPException(status_code=503, detail=result)


@app.get("/", response_class=HTMLResponse)
async def root():
    html = """
<html>
    <head>
        <title>LaTeX to PDF API - Usage</title>
    </head>
    <body>
        <h1>LaTeX to PDF API</h1>
        <p>Exemplo de chamada usando <strong>curl</strong>:</p>
        <pre>curl -X POST "https://thigas88-latex-api.hf.space/compile" \
         -H "Content-Type: application/json" \
         -d '{"content": "\\documentclass{article}\\begin{document}Hello World!\\end{document}"}' \
         --output document.pdf</pre>
        <p>Substitua a URL pela do seu servidor quando necessário.</p>
    </body>
</html>
"""
    return HTMLResponse(content=html)
