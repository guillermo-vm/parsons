import logging
import yaml
from typing import Any, Optional, Dict
from dataclasses import dataclass
from google.genai import types



logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result containers
# ---------------------------------------------------------------------------

@dataclass
class ServiceResult:
    """
    Base result — the runner only ever touches these fields.
    Rule: `output` is always the value meant to flow into the next step.
    """
    service_name: str
    status: str = "error"       # "success" | "partial" | "error"
    output: Any = None          # canonical downstream value — always set this
    raw_response: Any = None    # full SDK response, for deep debugging


@dataclass
class ResearchResult(ServiceResult):
    """
    ResearchService result.
    output  = raw text from the grounded search (fed into the next step)
    links   = rendered grounding links (side-channel, not passed downstream)
    """
    links: Optional[str] = None


@dataclass
class StructureResult(ServiceResult):
    """
    StructureService result.
    output = response.parsed — the typed, structured object
    No extra fields needed yet; subclass exists for consistency and future extension.
    """
    pass


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class BaseAIService:
    SERVICE_KEY = "base"

    # Hardcoded defaults — lowest priority layer
    defaults: Dict[str, Any] = {
        "temperature": 0.0,
        "model_id": "gemini-2.5-flash-lite",
        "safety_settings": [
            {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
    }

    # Subclasses declare their tools here — no __init__ / _build_config override needed
    tools: Optional[list] = None

    # Allowlist of valid GenerateContentConfig fields
    _SDK_PARAMS = {
        "candidate_count", "max_output_tokens", "presence_penalty",
        "frequency_penalty", "response_mime_type", "response_schema",
        "safety_settings", "stop_sequences", "system_instruction",
        "temperature", "top_k", "top_p", "tools",
    }

    def __init__(
        self,
        client: Any,
        service_config_override: Optional[Dict] = None,
        config_path: str = "config.yaml",
    ):
        self.client = client
        self.config_path = config_path

        yaml_data = self._load_yaml_config()
        global_settings  = yaml_data.get("global", {})
        service_settings = yaml_data.get(self.SERVICE_KEY, {})

        # Merge: defaults -> global YAML -> service YAML -> runtime override
        self.config: Dict[str, Any] = {
            **self.defaults,
            **global_settings,
            **service_settings,
            **(service_config_override or {}),
        }

        self.model_id = self.config.pop("model_id")


    # ------------------------------------------------------------------
    # Public entry point — the runner calls this, never perform() directly
    # ------------------------------------------------------------------

    def process(self, **kwargs) -> ServiceResult:
        """Unified entry point. Wraps perform() and guarantees a ServiceResult."""
        try:
            return self.perform(**kwargs)
        except Exception as e:
            logger.error(f"{self.SERVICE_KEY} unhandled error: {e}", exc_info=True)
            return ServiceResult(service_name=self.SERVICE_KEY, status="error", output=str(e))

    def perform(self, **kwargs) -> ServiceResult:
        """Override in every subclass. Must return the appropriate ServiceResult subclass."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement perform()")

    # ------------------------------------------------------------------
    # Shared config builder — subclasses pass extra kwargs, never override this
    # ------------------------------------------------------------------

    def _build_config(self, **kwargs) -> types.GenerateContentConfig:
        """
        Merges self.config with call-time overrides, injects class-level tools,
        hydrates safety dicts, filters to SDK params, and returns a
        ready-to-use GenerateContentConfig.
        """
        config = {**self.config, **kwargs}

        # Inject class-level tools unless the caller supplied their own
        if self.tools and "tools" not in kwargs:
            config["tools"] = self.tools

        # Hydrate safety setting dicts into SDK objects
        if "safety_settings" in config:
            config["safety_settings"] = [
                types.SafetySetting(**s) if isinstance(s, dict) else s
                for s in config["safety_settings"]
            ]

        params = {k: v for k, v in config.items() if k in self._SDK_PARAMS}
        return types.GenerateContentConfig(**params)

    def _load_yaml_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, "r") as f:
                data = yaml.safe_load(f)
                return data if isinstance(data, dict) else {}
        except (FileNotFoundError, yaml.YAMLError):
            logger.warning(f"Could not load {self.config_path}; using defaults only.")
            return {}


# ---------------------------------------------------------------------------
# ResearchService — Google Search grounding
# ---------------------------------------------------------------------------

class ResearchService(BaseAIService):
    SERVICE_KEY = "research_service"

    # _build_config picks this up automatically
    tools = [types.Tool(google_search=types.GoogleSearch())]

    def perform(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        config_override: Optional[Dict[str, Any]] = None,
    ) -> ResearchResult:
        """Runs a grounded Google Search via Gemini.

        result.output = raw text  ->  flows into the next pipeline step
        result.links  = grounding links  ->  side-channel, not passed downstream
        """
        result = ResearchResult(service_name=self.SERVICE_KEY)

        extra = {**(config_override or {})}
        if system_instruction:
            extra["system_instruction"] = system_instruction

        active_config = self._build_config(**extra)

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=active_config
            )
            result.raw_response = response

            text, links = self._extract_output(response)
            result.output = text or "No research results found. "
            result.links  = links or "No links found"
            result.status = "success" if text else "partial"

        except Exception as e:
            logger.error(f"ResearchService failed for prompt '{prompt}': {e}", exc_info=True)
            result.status = "error"
            result.output = "Research failed."

        return result

    def _extract_output(self, response) -> tuple[str, Optional[str]]:
        """Safely pulls text and grounding links out of the SDK response."""
        text = None
        try:
            if response.candidates and response.candidates[0].content.parts:
                text = response.text.strip()
        except (AttributeError, IndexError):
            pass

        links = None
        try:
            metadata = response.candidates[0].grounding_metadata
            if metadata and metadata.search_entry_point:
                links = metadata.search_entry_point.rendered_content
        except (AttributeError, IndexError) as e:
            logger.warning(f"Grounding metadata extraction failed: {e}")

        return text, links


# ---------------------------------------------------------------------------
# StructureService — structured JSON output via response_schema
# ---------------------------------------------------------------------------

class StructureService(BaseAIService):
    SERVICE_KEY = "structure_service"

    def perform(
        self,
        prompt: str,
        response_schema: Any,
        response_mime_type: str = "application/json",
        system_instruction: Optional[str] = None,
        config_override: Optional[Dict[str, Any]] = None,
    ) -> StructureResult:
        """Structures free text into a typed object defined by response_schema.

        result.output = response.parsed  ->  the typed, structured object
        """
        result = StructureResult(service_name=self.SERVICE_KEY)

        extra = {
            "response_schema": response_schema,
            "response_mime_type": response_mime_type,
            **({"system_instruction": system_instruction} if system_instruction else {}),
            **(config_override or {}),
        }
        active_config = self._build_config(**extra)

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=active_config
            )
            result.raw_response = response

            if response.parsed is None:
                finish_reason = getattr(
                    response.candidates[0] if response.candidates else None,
                    "finish_reason", "UNKNOWN"
                )
                logger.error(
                    f"StructureService: empty parse. finish_reason={finish_reason} | "
                    f"raw={getattr(response, 'text', '')}"
                )
                result.status = "error"
            else:
                result.status = "success"
                result.output = response.parsed

        except Exception as e:
            logger.error(
                f"StructureService error: {e} | model={self.model_id} | "
                f"schema={type(response_schema).__name__}",
                exc_info=True,
            )
            result.status = "error"

        return result




if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from dataclasses import dataclass
    from google import genai

    load_dotenv()
 
    # -- client ----------------------------------------------------------------
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    PROMPT = "What is the capital of France?"
 
    # -- ResearchService -------------------------------------------------------
    print("\n--- ResearchService ---")
    research_svc    = ResearchService(client=client)
    research_result = research_svc.process(prompt=PROMPT)
    print(f"status : {research_result.status}")
    print(f"output : {str(research_result.output)[:200]}")
    print(f"links  : {'present' if research_result.links else 'none'}")
 
    # -- StructureService ------------------------------------------------------
    print("\n--- StructureService ---")
 
    @dataclass
    class CapitalAnswer:
        country: str
        capital: str
 
    structure_svc    = StructureService(client=client)
    structure_result = structure_svc.process(
        prompt=f"Answer this: {PROMPT}. Return the country asked about and its capital.",
        response_schema=CapitalAnswer,
    )
    print(f"status : {structure_result.status}")
    print(f"output : {structure_result.output}")