"""JSON Schema для structured output на границах LLM.

Каждый экстрактор определяет свою локальную Pydantic-модель "что должен
вернуть LLM" (осознанно отдельную от core.models — LLM не должен ни знать,
ни придумывать служебные поля вроде doc_id/source_doc_id, их проставляет код
после вызова). Эта функция — единственное место, которое знает, как достать
JSON Schema из такой модели.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


def schema_for(model: type[BaseModel]) -> dict[str, Any]:
    return model.model_json_schema()
