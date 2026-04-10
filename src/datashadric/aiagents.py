# -*- coding: utf-8 -*-
"""
AI Agents Functions and Classes Module
Comprehensive collection of AI agent utilities for data analysis, natural language processing, and more.
"""

# OS and environment imports
import importlib
import io
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
        "You are an expert Data Scientist, and you are given a task to Identify and describe any outlier or anomalous points in this plot, we want to have well-defined data, that fits trends that are easy to visualise inorder to aid in gaining insights from the experiment. "
        "The outliers are often as follows: "
        "1) points that deviate significantly from the overall trend or pattern in the data, and/or "
        "2) points that lie on a purely vertical trend line usually at the end of the plot (towards the right of the image), and/or "
        "3) sometimes, the outliers are small (tight) point clouds that occur some distance from the rest of the scatter trend. "
        "In addition, assess other types of outliers in analytical fashion as per your knowledge as a data scientist. "
        "Wherever possible, estimate their coordinates or describe their location, such that it is easy to either 1) create anomalous point clouds in the form of boundary boxes for the points that are anomalous, so as to remove them in bulk and/or 2) identify each point by it's coordinates and thus make it removable from the dataset. "
        "In your output, be concise and only focus on the anomalies. In fact give me the bounding boxes in the Example format: boxes = [(x1, y1, x2, y2), ...] separated by a line skip before you start giving that portion of output, this will allows me to directly look for it and get data from it"
    )


def _extract_boxes(description: str):
    match = re.search(r"boxes\s*=\s*\[(.*?)\]", description, re.DOTALL)
    if not match:
        print("\n✗ No boxes found in AI output, using default")
        return [(100, 150, 120, 170)]

    boxes_str = match.group(1)
    try:
        boxes = ast.literal_eval(f"[{boxes_str}]")
        print(f"\n✓ Extracted boxes from AI output: {boxes}")
        return boxes
    except Exception as error:
        print(f"\n✗ Failed to parse boxes: {error}")
        return [(100, 150, 120, 170)]


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

    boxes = _extract_boxes(description)
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