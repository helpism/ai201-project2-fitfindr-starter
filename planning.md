# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Searches the mock listings database to find secondhand items that match a user's natural language description, with optional filters for size and price.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): A natural language search string describing the item (e.g., "vintage graphic tee" or "90s track jacket")
- `size` (str): A string to filter items by size (e.g., "M", "L", or "W30")
- `max_price` (float):  numeric ceiling to filter items by their "price" field

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->
A list of dictionaries, where each dictionary represents a single item listing. Each dictionary contains the following keys: id, title, description, category, style_tags, size, condition, price, colors, brand, and platform.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
If no results match the criteria, the groq model notifies the user that no items were found. It may suggest broadening the search by increasing the price limit or using more general style terms.
---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Analyzes a specific thrifted item and the user's existing wardrobe to generate 1–2 complete outfit recommendations

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): The full dictionary of the selected thrifted item found in the previous step.
- `wardrobe` (dict): ...
A dictionary containing the user's current closet items, following the  format defined in the wardrobe schema.
**What it returns:**
<!-- Describe the return value -->
A string providing a descriptive styling guide. This string details how to pair the new item with 1–2 specific pieces from the user's wardrobe to create a cohesive look.
**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->
If the wardrobe is empty or no compatible items are found, the agent informs the user and provides generic styling advice based on the item's "style_tags" (e.g., suggesting basic items like white tees or jeans that would match the piece)
---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Produces a short, shareable "fit card" caption for the final outfit to highlight the thrifted find.
**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (str): the styled outfit description produced by the suggest_outfit tool
`new_item` (dict): The dictionary containing the details (title, brand, and price) of the thrifted item.
**What it returns:**
<!-- Describe the return value -->
A string representing a catchy, social-media-ready caption. This typically includes the item's name, emojis, and a brief highlight of why the outfit works (e.g., "Scored these Vintage Levi's 501s for $38! Styling them with my chunky sneakers for a streetwear vibe")

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->
If the outfit input is missing or incomplete, the agent defaults to a standard "New Find" caption that highlights only the details of the new_item
---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->
Think: The agent looks at the user's query and its system instructions to decide which tool to call first (usually the search tool).
Action: Based on its thought, the agent selects the appropriate tool and provides the exact parameters.For example: search_listings(description="vintage tee", max_price=30.0).
Observation: The agent "observes" the raw data returned by the tool (the specific JSON list of shirts found in listings)
Record: It takes the tool's output and saves it to the session state. It then loops back to the thinking step to decide the next move.
---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->
As each tool finishes its task—for example, finding a vintage jacket—the agent writes that specific result into the session dictionary. When the next tool needs to know what jacket was found to suggest an outfit, the agent simply looks at its notes and passes the correct details along.
---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Agent informs the user and suggests adjusting filters (e.g., "Try searching for a different size or increasing your budget")|
| suggest_outfit | Wardrobe is empty | Agent generates styling advice based on the item's style_tags and category instead of specific wardrobe pairings|
| create_fit_card | Outfit input is missing or incomplete | Agent produces a generic "New Find" caption highlighting only the item's title, price, and brand|

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->
```mermaid
     graph TD
     %% Entry Point
     Start([User Query]) --> Loop[Agent Planning Loop]
     
     subgraph "Planning & State Management"
     Loop --> Tool1[search_listings(description, size, max_price)]
     
     %% Branching for Search Results
     Tool1 --> Check{Results found?}
     
     Check -- No --> Error[Set Error: No listings found and Update Session]
     Check -- Yes --> Update1[Session Update: selected_item = results]
     
     %% Sequential Tool Execution
     Update1 --> Tool2[suggest_outfit(selected_item, wardrobe)]
     Tool2 --> Update2[Session Update: outfit_suggestion = result]
     
     Update2 --> Tool3[create_fit_card(outfit_suggestion, selected_item)]
     Tool3 --> Update3[Session Update: fit_card = result]
     end
     
     %% Final Outputs
     Update3 --> End([Return Completed Session])
     Error --> End
     
     %% Visual connection back to UI
     End --> UI[Gradio Interface: Display found item, style guide, and card]
```
---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**

**Milestone 4 — Planning loop and state management:**

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->
The agent calls search_listings(description="vintage graphic tee", max_price=30.0)
**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->
The agent calls suggest_outfit(new_item=lst_006, wardrobe=example_wardrobe). It sees the user has "Baggy straight-leg jeans" (w_001) and "Chunky white sneakers" (w_007)
. It returns: "Pair this 2003 Tour tee with your baggy dark wash jeans and chunky white sneakers for a full streetwear vibe."
**Step 3:**
<!-- Continue until the full interaction is complete -->

**Final output to user:**
<!-- What does the user actually see at the end? -->
The three resulting pieces of data are displayed in the Gradio interface: the listing for the tee, the styling guide, and caption featuring emojis and hashtags that summarize the "win" of the thrifted find