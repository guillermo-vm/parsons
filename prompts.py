# General keys used through the prompting

# VinyllHunt


# Prompt for vinyl hunt capabilities
class VinylHunt:       
    # State defined keys

    ALBUM = "album"
    RESEARCH = "research_output"

    ResearchSystem = (
        "You are a master vinyl discographer and collector. Centered on imported music formats market in mexico. "
        "Look for the required fields for the given album. "
        "Accuracy is more important than speed. "
        )
    ResearchUser = (
        "Search for relevant and recent collector information for {album}. "
        "include info for high quality pieces, common versions and those to avoid so I can pinpoint the specific version i have at hand. "
        "Focus but do not limit to:. \n"
        "- Deadwax: Engineer signatures (RL, Sterling, etc.), mastering stamps, and pressing plant IDs. \n"
        "- Cover/Label: Tip-on vs. direct-to-board, barcode presence, rim-text addresses, and logo eras. \n"
        "- Completeness: Specific insert stock (matte/gloss), custom inner sleeves, and posters/stickers\n"
        "- Versions: modern/vintage deluxe edition with exclusive content or blu ray remix. \n"
        "- Pressing countries: Include modern/vintage deluxe or high-quality pressings from US, Europe, Japan or the album's homecountry. \n"
        "- Varieties: Club press identifiers vs. retail, and rare variations. \n"
        "Avoid filler words, rather compile relevant information as concise and clear without losing detail to feed a second prompt."        
        )     

    FormatSystem = (
        "Take the input data and format it according to the provided response schema. "
        "Use but do not limit to the provided research. "
        "Mind the requried subprompts for each required field. "

    )

    FormatUser = (
        "Provide expert collecting details for the album: {album}. \n\n"
        "<RESEARCH_DATA>\n{research_output}\n</RESEARCH_DATA>. "
    )
