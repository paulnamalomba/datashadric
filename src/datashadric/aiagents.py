# -*- coding: utf-8 -*-
"""
AI Agents Functions and Classes Module
Comprehensive collection of AI agent utilities for data analysis, natural language processing, and more.
"""

# OS and environment imports
import importlib
import io
import json
import os

# Typing and formatting imports
from typing import Any
import ast
import re

# Some imports from datashadric package
import datashadric.dataframing as dsdf
import datashadric.plotters as dsplt


DEFAULT_TEXT_MODEL = "gemma-4-31b-it"
DEFAULT_VISION_MODEL = DEFAULT_TEXT_MODEL
VISION_FALLBACK_MODEL = "gemini-2.5-flash"
DEFAULT_IMAGE_MODEL = "gemini-2.5-flash-image-preview"


def _get_google_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY or GOOGLE_API_KEY for Google GenAI access.")
    return api_key


def _get_google_genai_modules() -> tuple[Any, Any]:
    google_genai = importlib.import_module("google.genai")
    google_types = importlib.import_module("google.genai.types")
    return google_genai, google_types


def _get_google_client() -> Any:
    google_genai, _ = _get_google_genai_modules()
    return google_genai.Client(api_key=_get_google_api_key())


def _get_pil_image_module() -> Any:
    return importlib.import_module("PIL.Image")


def _generate_content(
    contents: Any,
    model: str,
    max_tokens: int | None = None,
    fallback_model: str | None = None,
):
    client = _get_google_client()
    config = None
    if max_tokens is not None:
        _, google_types = _get_google_genai_modules()
        config = google_types.GenerateContentConfig(maxOutputTokens=max_tokens)

    try:
        return client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )
    except Exception:
        if fallback_model and fallback_model != model:
            return client.models.generate_content(
                model=fallback_model,
                contents=contents,
                config=config,
            )
        raise


def _load_image(image_path: str) -> Any:
    pil_image_module = _get_pil_image_module()
    with pil_image_module.open(image_path) as image:
        return image.copy()


def _default_outlier_prompt() -> str:
    return (
        "You are an expert Data Scientist performing visual data cleaning on a plotted dataset. Your task is to identify and mathematically bound anomalous data regions in the provided chart using the chart's own data coordinates rather than pixel coordinates. "
        "The analysis must remain domain-agnostic: infer context from the axis labels, scale, and visible trend instead of assuming a specific field such as structural testing, finance, biology, or industrial monitoring. "
        "Typical anomalies may include: "
        "1) disconnected points or low-value floor scatter that sit away from the main trend, "
        "2) saturation walls or edge clusters where one variable appears clipped while logging continued, "
        "3) small rogue clusters separated from the dominant manifold, and "
        "4) abrupt discontinuities, jumps, or clearly non-physical regions relative to the main pattern in the plot. "
        "Do not guess blindly. Process the image methodically: identify the axes and approximate scale, briefly describe the valid manifold or dominant trend, then localize anomalous regions and estimate a slightly buffered bounding box around each anomalous cluster in graph data coordinates. "
        "Provide your final output exclusively as valid JSON with keys reasoning and boxes. The reasoning value must be a concise string explaining the anomaly localization logic. The boxes value must be a list of four-float lists in the form [x_min, y_min, x_max, y_max]. Do not include markdown formatting or any extra text outside the JSON object."
    )


def _normalize_boxes(raw_boxes: Any) -> list[tuple[float, float, float, float]]:
    normalized_boxes = []
    for box in raw_boxes:
        if not isinstance(box, (list, tuple)) or len(box) != 4:
            continue
        try:
            normalized_boxes.append(tuple(float(value) for value in box))
        except (TypeError, ValueError):
            continue
    return normalized_boxes


def _extract_analysis_payload(description: str) -> dict[str, Any]:
    cleaned_description = description.strip()
    if cleaned_description.startswith("```"):
        cleaned_description = re.sub(r"^```(?:json)?\s*", "", cleaned_description)
        cleaned_description = re.sub(r"\s*```$", "", cleaned_description)

    json_candidates = [cleaned_description]
    json_match = re.search(r"\{.*\}", cleaned_description, re.DOTALL)
    if json_match:
        json_candidates.append(json_match.group(0))

    for candidate in json_candidates:
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue

        if isinstance(payload, dict):
            boxes = _normalize_boxes(payload.get("boxes", []))
            reasoning = payload.get("reasoning")
            if boxes:
                print(f"\n✓ Extracted JSON analysis payload with {len(boxes)} box(es)")
                return {
                    "reasoning": reasoning.strip() if isinstance(reasoning, str) else None,
                    "boxes": boxes,
                }

    match = re.search(r"boxes\s*=\s*\[(.*?)\]", description, re.DOTALL)
    if match:
        boxes_str = match.group(1)
        try:
            boxes = _normalize_boxes(ast.literal_eval(f"[{boxes_str}]"))
            if boxes:
                print(f"\n✓ Extracted legacy boxes from AI output: {boxes}")
                return {"reasoning": None, "boxes": boxes}
        except Exception as error:
            print(f"\n✗ Failed to parse legacy boxes: {error}")

    print("\n✗ No valid JSON or legacy boxes found in AI output, using default")
    return {
        "reasoning": None,
        "boxes": [(100.0, 150.0, 120.0, 170.0)],
    }


def _analyze_plot_with_boxes(
    df: Any = None,
    excel_path=None,
    image_path=None,
    col_x=None,
    col_y=None,
    prompt: str = "",
    model: str = DEFAULT_VISION_MODEL,
):
    ai_provider = "google"
    if df is None:
        if excel_path is None:
            raise ValueError("excel_path is required when df is not provided.")
        df = dsdf.df_load_dataset(excel_path)

    if image_path is None:
        dsplt.df_scatter_plotter(df, col_x, col_y, save_path="temp_plot.png")
        image_path = "temp_plot.png"

    image = _load_image(image_path)
    if not prompt:
        prompt = _default_outlier_prompt()

    response = _generate_content(
        contents=[prompt, image],
        model=model,
        fallback_model=VISION_FALLBACK_MODEL,
    )

    print(df.head())
    print(f"Analyzing plot image using {ai_provider.upper()}...")
    description = (response.text or "").strip()
    print("AI analysis:\n", description)

    analysis_payload = _extract_analysis_payload(description)
    reasoning = analysis_payload["reasoning"]
    boxes = analysis_payload["boxes"]
    if reasoning:
        print("AI reasoning:\n", reasoning)
    if boxes:
        points_removed = 0
        print(f"  Original dataset: {len(df)} rows")
        for box in boxes:
            x_min, y_min, x_max, y_max = box
            print(f"x_min: {x_min}")
            print(f"x_max: {x_max}")
            print(f"y_min: {y_min}")
            print(f"y_max: {y_max}")
            print(
                f"\nRemoving points where X is between {x_min} and {x_max}, and Y is between {y_min} and {y_max}"
            )
            mask = (
                (df[col_x] >= x_min)
                & (df[col_x] <= x_max)
                & (df[col_y] >= y_min)
                & (df[col_y] <= y_max)
            )
            points_removed += mask.sum()
            df = df[~mask]

        dsplt.df_scatterplot_boundingboxes_plotter(
            df,
            col_x,
            col_y,
            boxes,
            title="Plot with Bounding Boxes",
            save_path="temp_plot_with_boxes.png",
        )
        print(f"\033[91m    Found {points_removed} anomalous points to remove\033[0m")
        print(f"\033[91m    Cleaned dataset: {len(df)} rows ({points_removed} rows removed)\033[0m")
    else:
        print("No valid boxes to process")

    print("_" * 75)
    return df


def ai_generate_text(prompt: str, model: str = DEFAULT_TEXT_MODEL, max_tokens: int = 150) -> str:
    """Generate text using Google's Gemma text model via google.genai."""
    response = _generate_content(prompt, model=model, max_tokens=max_tokens)
    return (response.text or "").strip()


def ai_generate_image(prompt: str, model: str = DEFAULT_IMAGE_MODEL, size: str = "1024x1024") -> Any:
    """Generate an image while keeping Gemini image-preview as the default image model."""
    client = _get_google_client()
    _, google_types = _get_google_genai_modules()
    pil_image_module = _get_pil_image_module()
    response = client.models.generate_images(
        model=model,
        prompt=prompt,
        config=google_types.GenerateImagesConfig(
            numberOfImages=1,
            imageSize=size,
        ),
    )

    if not response.generated_images or not response.generated_images[0].image:
        raise ValueError(f"No image data was returned by model {model}.")

    image_bytes = response.generated_images[0].image.image_bytes
    if not image_bytes:
        raise ValueError(f"Model {model} returned an image response without bytes.")

    with pil_image_module.open(io.BytesIO(image_bytes)) as image:
        return image.copy()


def ai_visual_recognition(image_path: str, model: str = DEFAULT_VISION_MODEL) -> str:
    """Perform visual recognition using Gemma 4 first, with Gemini flash fallback for images."""
    image = _load_image(image_path)
    response = _generate_content(
        contents=["Describe this image in detail.", image],
        model=model,
        fallback_model=VISION_FALLBACK_MODEL,
    )
    return (response.text or "").strip()


def ai_analyze_plot_data_with_vision(
    df: Any = None,
    excel_path=None,
    image_path=None,
    col_x=None,
    col_y=None,
    prompt: str = "",
    model: str = DEFAULT_VISION_MODEL,
) -> str:
    """Analyze plot data with Gemma 4 first, with Gemini flash fallback for image inputs."""
    return _analyze_plot_with_boxes(
        df=df,
        excel_path=excel_path,
        image_path=image_path,
        col_x=col_x,
        col_y=col_y,
        prompt=prompt,
        model=model,
    )

def ai_analyze_plot_data_with_bounding_boxes(
    df: Any = None,
    excel_path=None,
    image_path=None,
    col_x=None,
    col_y=None,
    prompt: str = "",
    model: str = DEFAULT_VISION_MODEL,
) -> str:
    """Analyze a plot and remove outlier regions using AI-generated bounding boxes."""
    return _analyze_plot_with_boxes(
        df=df,
        excel_path=excel_path,
        image_path=image_path,
        col_x=col_x,
        col_y=col_y,
        prompt=prompt,
        model=model,
    )


def ai_data_insights_summary(
    df: Any,
    prompt: str | None = None,
    model: str = DEFAULT_TEXT_MODEL,
    max_tokens: int = 600,
) -> str:
    """Generate a data insights summary using Gemma 4 text generation."""
    data_summary = df.describe().to_string()
    if prompt is None:
        prompt = (
            "Provide a concise summary of key insights from the data summary, focus on the deep insights and metrics that describe the data, the relationships between features and which features predict each other. Also, give us which features are redundant and which are not contributing to the model as well as those that high high direct contribution to outcomes. You can make each section easy to read and produce a .md of the insights for the data but also output the insights to the shell for the analyst to quickly visualise."
        )

    full_prompt = f"Given the following data summary:\n{data_summary}\n\n{prompt}"
    response = _generate_content(full_prompt, model=model, max_tokens=max_tokens)
    return (response.text or "").strip()