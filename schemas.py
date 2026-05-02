from pydantic import BaseModel, Field
from typing import List, Dict

# Define and constrict sub-prompts by record field, each particularity of a record is a sub-prompt
class VinylHuntResponseFormat(BaseModel):
    album_name: str = Field(
        description="Full album name. (e.g., 'Synchronicity')"
    )
    artist: str = Field(
        description="Full artist name. (e.g., 'The Police')"
    )

    # Changed to List[str] for a cleaner 'Tier List' structure
    mix_deadwax_info: List[str] = Field(
            description=(
                "Focus ONLY on 'Heavy Difference' inscriptions that determine audio value. "
                "1. Identify Mastering Engineer initials (e.g., 'RL', 'LH', 'GP', 'PORKY'). "
                "2. Identify Pressing Plant symbols (e.g., 'MR' circle for Monarch, 'P' for Pitman). "
                "3. Identify Record Club indicators to avoid (e.g., 'CRC', 'RCA Music Service'). "
                "Rank them as: [S-Tier, A-tier, B-tier] for top-tier sound, [Avoid] for inferior club/reissue cuts."
                "Always mention what each inscriptions reads. (RL, CRC)."
                "Briefly describe (one sentence) why each inscription is prefered or avoieded."
            )
        )

    cover_info: str = Field(
        description=(
            "Details to identify original vs. repress covers. "
            "Mention stripe order, barcodes, and rare art variations (like the nude photo or negative band shots)."
        )
    )
    center_label: str = Field(
        description="Identify center labels, records studio and pressing adress, mainly to help discern between originals, reissue and club editions"
    )

    insert_info: str = Field(
        description="List non-obvious inserts like posters, custom lyric sheets, or specific hype stickers."
    )

    sleeve_info: str = Field(
        description="Detail original inner sleeve stock (heavy vs thin) and art variations."
    )

    variation_info: str = Field(
        description="Note rare vinyl variations like translucent wax, specific misprints and limited editions."
    )

    version_explore: List[str] = Field(
        description=(
            "List generally obtainable better versions of the same record, pressed in the US, Europe, Japan, Mexico or album´s homecountry. "
            "For example if there exists a modern/vintage deluxe edition with exclusive content or blu ray remix."
            "Limit to up to top 5  entries. Include price, source (Analog vs. Digital), availability and special feautres (which exclusive content, which color vinyl etc)."
            "Always mention first the formats included in each edition e.g (Vynil, Vynil + Blu-Ray)."
        )
    )