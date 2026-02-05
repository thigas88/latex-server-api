import os
import subprocess
import uuid
import shutil
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
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
    return {"status": "healthy"}
