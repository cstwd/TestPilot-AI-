"""Optional AI source understanding, alongside the existing static AST result."""
import json
from .model_provider import provider
from .model_protocol import Understanding


def understand(files, target, *, normal=None, boundary=None, exception_probe=None):
    request = {"files": {name:"\n".join(f"{i}: {line}" for i,line in enumerate(src.splitlines(),1))
                         for name,src in files.items()}, "target":target, "normal":normal,
               "boundary":boundary, "exception_probe":exception_probe}
    instruction = (
        "Return only the schema object. functions is a sorted list of 'filename.py:name' for top-level function "
        "definitions, never constants. parameters MUST be an array of three-element arrays: "
        '["name","annotation","default expression"]. Use JSON null if either is absent. '
        "Example: [[\"n\",\"int\",null],[\"flag\",\"bool\",\"True\"]]. Never use objects for parameters. "
        "branch_lines lists every explicit if/for/while/ternary in the target, including nested statements. "
        "Evaluate the normal call and put the actual resulting Python value in return_value. Evaluate the boundary "
        "call and put its actual result in boundary_value. Put the exception class raised by exception_probe in "
        "exception, or null if it succeeds. For example, if the boundary call produces False, boundary_value is "
        "the JSON boolean false, even if the call's argument is a number. Give the result value, not the call "
        "expression, argument or type name. If no call was requested use null for that answer. defect_line is the source line responsible "
        "for a mismatch with documented behavior, or null. Do not modify source."
    )
    messages=[{"role":"system","content":instruction},{"role":"user","content":json.dumps(request,ensure_ascii=False)}]
    return provider.infer("source-understanding", messages, Understanding, max_tokens=512)
