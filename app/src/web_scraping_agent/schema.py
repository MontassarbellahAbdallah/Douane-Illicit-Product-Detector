# Developed by Montassar Bellah Abdallah

from pydantic import BaseModel, Field
from typing import List, Optional, Union, get_type_hints, get_origin, get_args


class SingleExtractedProduct(BaseModel):
    page_url: Optional[str] = Field(title="The original url of the product page", default=None)
    product_title: Optional[str] = Field(title="The title of the product", default=None)
    product_image_url: Optional[str] = Field(title="The url of the product image", default=None)
    product_url: Optional[str] = Field(title="The url of the product", default=None)
    product_current_price: Optional[float] = Field(title="The current price of the product", default=None)
    product_original_price: Optional[float] = Field(title="The original price of the product before discount. Set to None if no discount", default=None)
    product_discount_percentage: Optional[float] = Field(title="The discount percentage of the product. Set to None if no discount", default=None)

    suspicion_score: Optional[int] = Field(title="Suspicion level of the product being illicit (1-10, where 10 is highly suspicious)", default=None)
    suspicion_reasons: List[str] = Field(title="Reasons why this product is flagged as potentially illicit or counterfeit", default_factory=list)


class AllExtractedProducts(BaseModel):
    products: List[SingleExtractedProduct]


def generate_schema_string(model):
    """Generate schema string from Pydantic model for LLM extraction."""
    schema_parts = []
    hints = get_type_hints(model)
    for field_name, field_type in hints.items():
        if get_origin(field_type) is list:
            inner_type = get_args(field_type)[0]
            if hasattr(inner_type, '__annotations__'):
                # Nested object array
                inner_parts = []
                inner_hints = get_type_hints(inner_type)
                for inner_name, inner_type in inner_hints.items():
                    type_str = "string" if inner_type == str else "number"
                    inner_parts.append(f"{inner_name}: {type_str}")
                schema_parts.append(f"{field_name}: [{{{', '.join(inner_parts)}}}]")
            else:
                type_str = "string" if inner_type == str else "number"
                schema_parts.append(f"{field_name}: [{type_str}]")
        else:
            if field_type == str:
                type_str = "string"
            elif field_type in (int, float):
                type_str = "number"
            else:
                # Optional types
                origin = get_origin(field_type)
                if origin is Union:
                    args = get_args(field_type)
                    if len(args) == 2 and type(None) in args:
                        non_none = args[0] if args[1] is type(None) else args[1]
                        type_str = "string" if non_none == str else "number"
                        type_str += " | null"
                    else:
                        type_str = "string"  # fallback
                else:
                    type_str = "string"  # fallback
            schema_parts.append(f"{field_name}: {type_str}")
    return "{" + ", ".join(schema_parts) + "}"
