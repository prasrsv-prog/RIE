from dataclasses import dataclass

from prompting.text_prompt_candidate import TextPromptCandidate


@dataclass(frozen=True)
class TextPromptCandidateCollection:
    prompt_candidates: list[TextPromptCandidate]
