# app/chatbot/tools.py

from sqlalchemy.orm import Session
from app.crud import crud_order, crud_product, crud_dashboard
from app.models import model

# --- Tool Functions ---

def get_user_profile(db: Session, current_user: model.User):
    """Fetches the profile information for the currently logged-in user."""
    return {"id": current_user.id, "email": current_user.email}

def get_last_order(db: Session, current_user: model.User):
    """Retrieves the details of the most recent order for the currently logged-in user."""
    last_order = crud_order.get_most_recent_order_by_user(db, user_id=current_user.id)
    if not last_order:
        return "You have no past orders."
    return {
        "order_id": last_order.id,
        "order_date": last_order.order_date.strftime("%Y-%m-%d"),
        "total_items": len(last_order.items)
    }

def get_product_details(db: Session, product_name: str):
    """Finds a product by its name and returns its details like SKU and stock quantity."""
    product = crud_product.get_product_by_name(db, name=product_name)
    if not product:
        return f"Sorry, I could not find a product named '{product_name}'."
    return {
        "name": product.name,
        "sku": product.sku,
        "category": product.category,
        "quantity_in_stock": product.currentStock,
        "reorder_point": product.reorderPoint,
        "supplier": product.supplier
    }

def study_data(db: Session, current_user: model.User):
    """
    Analyzes the inventory and returns key performance indicators (KPIs).
    Use this when the user asks for a summary, analysis, report, or to 'study the data'.
    """
    kpis = crud_dashboard.get_dashboard_kpis(db)
    return kpis

def get_capabilities(db: Session, current_user: model.User):
    """
    Provides a summary of all the assistant's capabilities.
    This should be called when the user asks for help or says hello.
    """
    return (
        "I am your inventory assistant. I can help you with the following tasks:\n"
        "- **Get Your Profile:** Ask 'What is my email?'\n"
        "- **Check Last Order:** Ask 'Tell me about my last order.'\n"
        "- **Find Product Info:** Ask 'What is the price or stock level of the High-Performance Laptop?'\n"
        "- **Study Your Data:** Ask 'Give me a summary of the inventory.' or 'Study my data.'"
    )

# --- Tool Definitions for the AI ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_capabilities",
            "description": "Explains what the assistant can do. Use this when the user greets you, asks for help, or asks what you can do.",
        },
    },
    {
        "type": "function",
        "function": {
            "name": "study_data",
            "description": "Analyzes the inventory and returns key performance indicators (KPIs) like total inventory value and low stock item counts.",
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_profile",
            "description": "Get the profile information of the current user, like their email.",
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_last_order",
            "description": "Get the most recent order details for the current user.",
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_details",
            "description": "Get information about a specific product, such as its SKU and stock level.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The name of the product to look up, e.g., 'High-Performance Laptop'",
                    }
                },
                "required": ["product_name"],
            },
        },
    }
]

# --- Mapping of Function Name to Actual Python Function ---
available_tools = {
    "get_capabilities": get_capabilities,
    "study_data": study_data,
    "get_user_profile": get_user_profile,
    "get_last_order": get_last_order,
    "get_product_details": get_product_details,
}