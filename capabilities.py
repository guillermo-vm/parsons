from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict
from enum import Enum

# Dependencies
import prompts
import schemas

# Add logger?

from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict, Callable



OUTPUT =  "output"

@dataclass
class WorkFlowStep:
    name : str
    service_type: str
    system_prompt: str
    user_prompt: str
    state_output_key: str # Where the step output will be saved in the State
    schema: Optional[Any] = None
    response_mime_type: Optional[str] = None
    # Called after this step runs — receives the result, returns next step name or None to stop
    # If None, runner just proceeds to the next step in order (linear default)
    on_result: Optional[Callable] = None # Callable for next step depending on result, deafult None
    state_input_keys: List[str] = field(default_factory=list) # Where step input locates in the state




@dataclass
class Parameter:
    name : str
    required : bool
    default: Any = None
    description: str = ""


@dataclass
class Recipe:
    name: str
    service_map : Dict[str, str]
    parameters: List[Parameter]
    steps: List[WorkFlowStep]  # ordered, but on_result can jump around


    def get_step(self, name: str) -> Optional[WorkFlowStep]:
        return next((s for s in self.steps if s.name == name), None)
    
    def get_defaults(self) -> Dict[str, Any]:
        return {p.name: p.default for p in self.parameters if p.default is not None}
    
    def validate_inputs(self, inputs: Dict[str,Any]):
        required = [p.name for p in self.parameters if p.required]
        for name in required:
            if name not in inputs or not inputs[name]:
                raise ValueError(f"Missing required parameter for {self.name}: {name}")
            


class Capability:
    def __init__(self, recipe: Recipe, services : Dict[str,Any]):
        self.recipe = recipe
        self.services = services

    def run(self,**user_kwargs) -> Dict[str,Any]:

        # Verify required parameters
        self.recipe.validate_inputs(user_kwargs)

        # Get state
        state = self.recipe.get_defaults()
        state.update(user_kwargs)


        result = None

        # Start with first step, then follow on_result hooks
        current_step = self.recipe.steps[0]

        while current_step is not None:
            # Get service to use, service are instanced at ai_engine
            service = self.services[current_step.service_type]

            # Extract inputs from state
            inputs = {k: state[k] for k in current_step.state_input_keys if k in state}



            to_process = {"prompt": current_step.user_prompt.format(**inputs),
                          "system_instruction": current_step.system_prompt.format(**inputs),     
                    }


            if current_step.schema and current_step.response_mime_type:
                to_process.update({
                    "response_schema": current_step.schema,
                    "response_mime_type": current_step.response_mime_type
                })


            result = service.process(**to_process)

            # Write on state
            state[current_step.state_output_key] = result.output if result.status != "error" else result.raw_response

            if current_step.on_result:
                # Hook returns a step name (str) or None to stop
                next_name = current_step.on_result(result)
                current_step = self.recipe.get_step(next_name) if next_name else None
                print(f"Sucsseful step: {current_step.name}")
            else:
                # Linear default: advance to next step in list
                idx = self.recipe.steps.index(current_step)
                current_step = self.recipe.steps[idx + 1] if idx + 1 < len(self.recipe.steps) else None

        return state


# --- Registry ---
VINYL_HUNT = Recipe(
    name = "vinyl_hunt",
    parameters= [
        Parameter(prompts.VinylHunt.ALBUM, required= True, description = "Full album name (album and artist, may include additional album info (e.g UK pressed))")
    ],

    service_map= {
        "search": "research_service",
        "structure": "structure_service"
    },

    steps = [
        #research step
        WorkFlowStep(
            name = "Vinyl web research",
            service_type = "research_service",
            system_prompt = prompts.VinylHunt.ResearchSystem,
            user_prompt = prompts.VinylHunt.ResearchUser,
            state_input_keys = [prompts.VinylHunt.ALBUM],
            state_output_key = prompts.VinylHunt.RESEARCH
        ),

        #structurize step
        WorkFlowStep(
            name = "Results strucutring and subprompting",
            service_type = "structure_service",
            system_prompt = prompts.VinylHunt.FormatSystem,
            user_prompt = prompts.VinylHunt.FormatUser,
            schema = schemas.VinylHuntResponseFormat,
            response_mime_type = "application/json",
            state_input_keys= [prompts.VinylHunt.ALBUM, prompts.VinylHunt.RESEARCH],
            state_output_key= OUTPUT

        )
    ]
)

SKILLS_REGISTRY = {
    "vinyl_hunt" : VINYL_HUNT
}

if __name__ == "__main__":
    import os
    from google import genai
    from services import ResearchService, StructureService
    from capabilities import VINYL_HUNT, Capability
    from dotenv import load_dotenv

    load_dotenv()
 
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
 
    services = {
        "research_service": ResearchService(client=client),
        "structure_service": StructureService(client=client),
    }
 
    vinyl_hunt = Capability(recipe=VINYL_HUNT, services=services)
 
    print("\n--- Vinyl Hunt Test ---")
    result = vinyl_hunt.run(album="Pink Floyd - The Dark Side of the Moon")
    print(f"Final output: {result}")
    print(result.keys())