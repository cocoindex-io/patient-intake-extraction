"""
Patient intake extraction (v1) — DSPy + Gemini vision.

Walk a folder of patient intake PDFs, render each page to an image, extract
structured patient information with a vision LLM via DSPy, and write one JSON
file per form. Re-runs only reprocess forms that actually changed.

Run:
    cocoindex update main.py
"""

from __future__ import annotations

import pathlib

import dspy
import pymupdf

import cocoindex as coco
from cocoindex.connectors import localfs
from cocoindex.resources.file import FileLike, PatternFilePathMatcher

from models import Patient


class PatientExtractionSignature(dspy.Signature):
    """Extract structured patient information from a medical intake form image."""

    form_images: list[dspy.Image] = dspy.InputField(
        desc="Images of the patient intake form pages"
    )
    patient: Patient = dspy.OutputField(
        desc="Extracted patient information with all available fields filled"
    )


class PatientExtractor(dspy.Module):
    """DSPy module for extracting patient information from intake form images."""

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.ChainOfThought(PatientExtractionSignature)

    def forward(self, form_images: list[dspy.Image]) -> Patient:
        result = self.extract(form_images=form_images)
        return result.patient


@coco.fn
def extract_patient(pdf_content: bytes) -> Patient:
    pdf_doc = pymupdf.open(stream=pdf_content, filetype="pdf")

    form_images = []
    for page in pdf_doc:
        pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
        form_images.append(dspy.Image(pix.tobytes("png")))

    pdf_doc.close()

    return PatientExtractor()(form_images=form_images)


@coco.fn(memo=True)
async def process_patient_form(file: FileLike, outdir: pathlib.Path) -> None:
    content = await file.read()
    patient_info = extract_patient(content)
    output_filename = file.file_path.path.stem + ".json"
    localfs.declare_file(
        outdir / output_filename,
        patient_info.model_dump_json(indent=2),
        create_parent_dirs=True,
    )


@coco.fn
async def app_main(sourcedir: pathlib.Path, outdir: pathlib.Path) -> None:
    files = localfs.walk_dir(
        sourcedir,
        path_matcher=PatternFilePathMatcher(included_patterns=["**/*.pdf"]),
    )
    await coco.mount_each(process_patient_form, files.items(), outdir)


lm = dspy.LM("gemini/gemini-2.5-flash")
dspy.configure(lm=lm)

app = coco.App(
    coco.AppConfig(name="PatientIntakeExtraction"),
    app_main,
    sourcedir=pathlib.Path("./data/patient_forms"),
    outdir=pathlib.Path("./output_patients"),
)
