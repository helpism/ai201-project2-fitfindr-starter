# FitFindr — Starter Kit

FitFindr is a personal shopping assistant that helps users find secondhand clothes and styles them with items they already own. It uses a Groq-powered agent to search a mock database, suggest outfits, and create social media captions. Courtesy of CodePath.

## Project File Structure

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── app.py                      # Main application entry point
├── tools.py                    # Tool functions for the agent
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

```bash
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

To run:
```bash
python app.py
```

## Tool Inventory

| Tool Name | Input Parameters | Output | Purpose |
|-----------|------------------|--------|---------|
| `search_listings` | `description` (str), `size` (str/None), `max_price` (float/None) | `list[dict]` | Searches the listings.json dataset for items that match keywords, size, and budget |
| `suggest_outfit` | `new_item` (dict), `wardrobe` (dict) | `str` | Takes a thrifted find and pairs it with 1–2 items from the user's closet to create a look |
| `create_fit_card` | `outfit` (str), `new_item` (dict) | `str` | Generates a short, catchy social media caption with emojis to highlight the new find |

## Planning Loop

The agent follows a ReAct (Reason + Act) loop to process user queries:

- **Think**: The agent looks at the query and decides which tool to call next based on what information is still missing.
- **Act**: It calls the tool with specific arguments (like a price cap or a category).
- **Observation**: It looks at the data the tool returns (like a list of shirts).
- **Record**: It saves the results into the session state and repeats the loop until the task is done.

## State Management

Information is passed between tools using a central Session Dictionary. When `search_listings` finds an item, the agent records it as the `selected_item`. This exact dictionary is then passed into `suggest_outfit` and `create_fit_card`, ensuring all tools are talking about the same piece of clothing without losing data.

## Error Handling

Handled specific failure points for each tool to keep the agent from crashing:

- **Search**: If no items match, the agent tells the user and suggests using broader terms.
- **Styling**: If the user's wardrobe is empty, the agent provides generic fashion advice based on the item's tags.
- **Captioning**: If no outfit was generated, the tool returns a specific error string: `"Error: Cannot create a fit card because no outfit suggestion was provided"`.

## Spec Reflection

The final implementation matches the original plan, especially the branching logic. If a search fails, the agent stops immediately instead of trying to style a non-existent item. The Gradio UI successfully displays all three parts of the session on separate panels.

## AI Usage

**Instance 1: Implementing tools.py**
- **Input**: Tool function signatures and descriptions from the "Tools" section.
- **Output**: A complete Python file with the three tool functions and the Groq client setup.
- **Explanation**: By providing exact function names and parameters, the AI wrote logic for the three main tools based on the planning document. The prompt ensured the AI used the correct Groq model for outfit suggestions and fit cards, while handling edge cases like an empty wardrobe.

**Instance 2: Fixing the Search Logic**
- **Input**: Mermaid architecture diagram and the "State Management" spec section.
- **Output**: A search function using strict phrase matching.
- **Change Made**: The initial search was too strict, it couldn't find a "vintage tee" unless the words were adjacent. The implementation was updated to split searches into separate keywords, fixing the search to return relevant listings instead of "no items found."

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

