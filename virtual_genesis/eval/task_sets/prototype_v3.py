PROTOTYPE_V3_TASKS = [
    # Boundary-heavy analytical tasks: less explicit keywords, more ambiguity
    "Given the two remediation notes below, determine which path is more defensible for a production review and justify your conclusion with the strongest available support.",
    "You are preparing a release recommendation: decide which proposal is safer and explain the decisive difference using the evidence provided.",
    "Review the two incident narratives and state which one better explains the outage, along with the most important supporting clue.",
    "For the final approval note, judge which migration option carries lower operational risk and support the judgment from the record.",
    "Between the two hypotheses below, indicate which one deserves more confidence and show the basis for that confidence.",
    "Choose the stronger of the two root-cause accounts and make the distinction explicit for an auditor.",

    # Harder synthesis: fragmented evidence, implicit need for grounding
    "Prepare a final incident update from the fragments below. The update must stay close to the evidence and avoid unsupported claims.",
    "Draft a concise executive answer from the notes below while making clear what is observed versus what is inferred.",
    "Turn the following fragments into one short status explanation that preserves the evidence trail.",
    "A reviewer needs one grounded answer from these scattered findings; write it without collapsing distinct pieces of support.",
    "Produce a compact recommendation from the material below, making sure every major point remains traceable to supporting detail.",
    "Write a single coherent conclusion from the observations below, but keep the support structure visible.",

    # Boundary procedural tasks: structured output need but less explicit cues
    "Prepare an operator handoff checklist from the raw details below, keeping the fields stable and easy to scan.",
    "Turn the record into a reusable handoff format with labeled values and a clean ordering.",
    "An operator needs this mess converted into a dependable checklist. Extract the important fields and normalize the layout.",
    "Rework the details below into a compact, repeatable handoff structure for the next shift.",
    "Build a clean field-oriented summary from the raw input below so that another operator can follow it quickly.",
    "Convert the unstructured details into a consistent checklist and preserve the key attributes without noise.",
]
