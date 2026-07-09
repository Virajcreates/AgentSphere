from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from agentsphere.ai.prompts.prompt_compiler import PromptCompiler
from agentsphere.ai.prompts.prompt_manager import PromptManager
from agentsphere.interfaces.container import ApplicationContainer

router = APIRouter(prefix="/api/v1/prompts", tags=["Prompts"])


class CompilePromptRequest(BaseModel):
    namespace: str = Field("default", description="Prompt namespace")
    name: str = Field(..., description="Prompt template name")
    variables: dict[str, Any] = Field(default_factory=dict, description="Variables context map")
    tenant_id: str | None = Field(None, description="Tenant override, if applicable")


class PromptDiffRequest(BaseModel):
    text_a: str = Field(..., description="Original string source")
    text_b: str = Field(..., description="Target comparison source")


@router.get("")
@inject
async def list_prompt_templates(
    prompt_manager: PromptManager = Depends(Provide[ApplicationContainer.ai.prompt_manager]),
) -> list[dict[str, Any]]:
    """Lists all active system-default templates."""
    results = []
    # Fetch from inner system dictionary: (namespace, name, version) -> template_str
    for (ns, name, ver), template in prompt_manager._system_templates.items():
        results.append({
            "namespace": ns,
            "name": name,
            "version": ver,
            "template": template,
        })
    return results


@router.post("/compile")
@inject
async def compile_prompt(
    request: CompilePromptRequest,
    compiler: PromptCompiler = Depends(Provide[ApplicationContainer.ai.prompt_compiler]),
) -> dict[str, Any]:
    """Compiles dynamic prompt variables recursively, outputting raw rendered prompts."""
    try:
        compiled = compiler.compile(
            namespace=request.namespace,
            name=request.name,
            variables=request.variables,
            tenant_id=request.tenant_id,
        )
        return {"compiled_text": compiled}
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Prompt compilation failed: {e!s}") from e


@router.post("/diff")
async def diff_prompts(request: PromptDiffRequest) -> dict[str, Any]:
    """Runs a simplistic side-by-side lines differences check for diff viewers."""
    lines_a = request.text_a.splitlines()
    lines_b = request.text_b.splitlines()

    diff_records = []
    max_len = max(len(lines_a), len(lines_b))
    for i in range(max_len):
        la = lines_a[i] if i < len(lines_a) else ""
        lb = lines_b[i] if i < len(lines_b) else ""
        diff_records.append({
            "line": i + 1,
            "original": la,
            "modified": lb,
            "is_different": la != lb,
        })
    return {"diff": diff_records}
