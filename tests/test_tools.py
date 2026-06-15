import pytest
from unittest.mock import MagicMock
import tools
from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe


#  Global Groq Mock Setup 

@pytest.fixture(autouse=True)
def setup_mock_groq(monkeypatch):
    """Mock the Groq API client globally for all tests."""
    mock_client = MagicMock()
    
    # Mock the nested response structure: response.choices[0].message.content
    mock_choice = MagicMock()
    mock_choice.message.content = "Mocked fashion advice: This look is a complete vibe! 🔥 #OOTD"
    
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    
    # Set the return value for the completions API call
    mock_client.chat.completions.create.return_value = mock_response
    
    # Replace the actual client initialization function with the mock
    monkeypatch.setattr(tools, "_get_groq_client", lambda: mock_client)


#  Search Listings Tests 

def test_search_returns_results():
    """Test searching with a standard valid query."""
    results = search_listings("tee", size=None, max_price=50.0)
    assert isinstance(results, list)
    assert len(results) > 0
    assert any("Tee" in item["title"] or "tee" in item["description"].lower() for item in results)


def test_search_empty_results():
    """Test searching with criteria that should yield zero matches."""
    results = search_listings("designer ballgown", size="XXS", max_price=5.0)
    assert results == []  


def test_search_price_filter():
    """Test searching with a maximum price cap filter."""
    max_p = 20.0
    results = search_listings("tee", size=None, max_price=max_p)
    assert all(item["price"] <= max_p for item in results)


#  Suggest Outfit Tests 

def test_suggest_outfit_with_wardrobe():
    """Test generating outfit suggestions using a populated wardrobe."""
    example_item = {
        "title": "Vintage Levi's 501s",
        "description": "Classic denim",
        "category": "bottoms",
        "style_tags": ["vintage", "streetwear"]
    }
    wardrobe = get_example_wardrobe()
    suggestion = suggest_outfit(example_item, wardrobe)
    
    assert isinstance(suggestion, str)
    assert len(suggestion) > 0


def test_suggest_outfit_empty_wardrobe():
    """Test generating outfit suggestions with an empty wardrobe input."""
    example_item = {
        "title": "90s Track Jacket",
        "description": "Athletic layer",
        "category": "outerwear",
        "style_tags": ["90s", "athletic"]
    }
    empty_wardrobe = get_empty_wardrobe() 
    suggestion = suggest_outfit(example_item, empty_wardrobe)
    
    assert isinstance(suggestion, str)
    assert len(suggestion) > 0


#  Create Fit Card Tests 

def test_create_fit_card_success():
    """Test caption generation with valid outfit text and item details."""
    example_item = {"title": "Vintage Levi's", "price": 38.0}
    outfit = "Pair these with your chunky white sneakers."
    
    caption = create_fit_card(outfit, example_item)
    assert isinstance(caption, str)
    assert len(caption) > 0


def test_create_fit_card_empty_input():
    """Test error string output when passsed an empty outfit string."""
    example_item = {"title": "Vintage Levi's", "price": 38.0}
    result = create_fit_card("", example_item)
    
    assert "Error" in result
    assert "no outfit suggestion was provided" in result