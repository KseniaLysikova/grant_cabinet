import json
import re
from threading import Lock

import torch
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"

_model = None
_tokenizer = None
_model_lock = Lock()


class AIReviewResult(BaseModel):
    score: int
    summary: str
    recommendations: str


def load_model():
    global _model, _tokenizer

    if _model is None or _tokenizer is None:
        with _model_lock:
            if _model is None or _tokenizer is None:
                _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
                _model = AutoModelForCausalLM.from_pretrained(
                    MODEL_NAME,
                    torch_dtype="auto",
                    device_map="auto"
                )
    return _model, _tokenizer


def extract_json(text: str) -> dict:
    text = text.strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("JSON not found in model output")

    return json.loads(match.group(0))


async def analyze_application(text: str, title: str) -> AIReviewResult:
    try:
        model, tokenizer = load_model()

        system_prompt = (
            "Ты помощник для оценки грантовых заявок. "
            "Отвечай только валидным JSON без пояснений, markdown и лишнего текста."
        )

        user_prompt = f"""
Проанализируй грантовую заявку.

НАЗВАНИЕ:
{title}

ТЕКСТ:
{text}

Оцени заявку по шкале 0-100 по критериям:
1. Четкость цели
2. Актуальность проблемы
3. Конкретность плана
4. Оригинальность идеи
5. Качество изложения

Верни строго JSON такого вида:
{{
  "score": число от 0 до 100,
  "summary": "краткий вывод на 1-2 предложения",
  "recommendations": "3 короткие рекомендации в одной строке"
}}
        """.strip()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        text_prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        model_inputs = tokenizer([text_prompt], return_tensors="pt").to(model.device)

        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=220,
            do_sample=False,
            temperature=0.1
        )

        generated_ids = [
            output_ids[len(input_ids):]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        result_text = tokenizer.batch_decode(
            generated_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True
        )[0].strip()

        result = extract_json(result_text)

        score = int(result.get("score", 50))
        score = max(0, min(100, score))

        summary = str(result.get("summary", "Средняя заявка")).strip()
        recommendations = str(
            result.get("recommendations", "Добавьте больше конкретики, целей и ожидаемых результатов")
        ).strip()

        return AIReviewResult(
            score=score,
            summary=summary,
            recommendations=recommendations
        )

    except Exception:
        return simple_heuristic_analysis(title, text)


def simple_heuristic_analysis(title: str, text: str) -> AIReviewResult:
    score = 50

    text_lower = text.lower()

    if len(title) < 10:
        score -= 10
    if len(text) < 100:
        score -= 15
    if any(word in text_lower for word in ["цель", "задача", "результат"]):
        score += 10
    if any(word in text_lower for word in ["инновация", "новый", "уникальный"]):
        score += 10
    if any(word in text_lower for word in ["план", "этап", "срок", "бюджет"]):
        score += 10
    if len(text.split(".")) < 3:
        score -= 10

    score = max(10, min(90, score))

    return AIReviewResult(
        score=score,
        summary=f"Заявка получила {score} баллов по локальной эвристической оценке.",
        recommendations=(
            "Добавьте больше конкретики по целям; "
            "опишите план реализации по этапам; "
            "уточните ожидаемые результаты и пользу проекта."
        )
    )
