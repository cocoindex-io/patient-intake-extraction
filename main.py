import tempfile
import dataclasses

from dotenv import load_dotenv
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered
from marker.config.parser import ConfigParser

import cocoindex

@dataclasses.dataclass
class Contact:
    name: str
    phone: str
    relationship: str

@dataclasses.dataclass
class Insurance:
    provider: str
    policy_number: str
    group_number: str | None
    policyholder_name: str
    relationship_to_patient: str

@dataclasses.dataclass
class Condition:
    name: str
    diagnosed: bool

@dataclasses.dataclass
class Medication:
    name: str
    dosage: str

@dataclasses.dataclass
class Allergy:
    name: str

@dataclasses.dataclass
class Surgery:
    name: str
    date: str

@dataclasses.dataclass
class Patient:
    name: str
    dob: str
    gender: str
    preferred_pronouns: str
    address: str
    city: str
    state: str
    zip_code: str
    phone: str
    email: str
    preferred_contact_method: str
    emergency_contact: Contact
    insurance: Insurance | None
    reason_for_visit: str
    symptoms_duration: str
    past_conditions: cocoindex.typing.List[Condition]
    current_medications: cocoindex.typing.List[Medication]
    allergies: cocoindex.typing.List[Allergy]
    surgeries: cocoindex.typing.List[Surgery]
    occupation: str | None
    pharmacy: Contact | None
    consent_given: bool
    consent_date: str | None


class PdfToMarkdown(cocoindex.op.FunctionSpec):
    """Convert a PDF to markdown."""

@cocoindex.op.executor_class(gpu=True, cache=True, behavior_version=1)
class PdfToMarkdownExecutor:
    """Executor for PdfToMarkdown."""

    spec: PdfToMarkdown
    _converter: PdfConverter

    def prepare(self):
        config_parser = ConfigParser({})
        self._converter = PdfConverter(create_model_dict(), config=config_parser.generate_config_dict())

    def __call__(self, content: bytes) -> str:
        with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as temp_file:
            temp_file.write(content)
            temp_file.flush()
            text, _, _ = text_from_rendered(self._converter(temp_file.name))
            return text



@cocoindex.flow_def(name="PatientIntakeExtraction")
def patient_intake_extraction_flow(flow_builder: cocoindex.FlowBuilder, data_scope: cocoindex.DataScope):
    """
    Define a flow that extracts patient information from intake forms.
    """
    data_scope["documents"] = flow_builder.add_source(cocoindex.sources.LocalFile(path="files", binary=True))

    patients_index = data_scope.add_collector()

    with data_scope["documents"].row() as doc:
        doc["markdown"] = doc["content"].transform(PdfToMarkdown())
        doc["patient_info"] = doc["markdown"].transform(
            cocoindex.functions.ExtractByLlm(
                llm_spec=cocoindex.LlmSpec(
                     api_type=cocoindex.LlmApiType.OLLAMA,
                     model="llama3.2"
                ),
                # Replace by this spec below, to use OpenAI API model instead of ollama
                #   llm_spec=cocoindex.LlmSpec(
                #       api_type=cocoindex.LlmApiType.OPENAI, model="gpt-4o"),
                output_type=Patient,
                instruction="Please extract patient information from the intake form."))
        patients_index.collect(
            filename=doc["filename"],
            patient_info=doc["patient_info"],
        )

    patients_index.export(
        "patients",
        cocoindex.storages.Postgres(table_name="patients_info"),
        primary_key_fields=["filename"],
    )

@cocoindex.main_fn()
def _run():
    pass

if __name__ == "__main__":
    load_dotenv(override=True)
    _run()