"""
Schema validation functionality.
"""
from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from jsonschema import validate as jsonschema_validate, ValidationError
from ..utils.logger import logger

def load_schema(schema_name: str = "brief_schema", schema_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Load a JSON schema from file.
    
    Args:
        schema_name: Name of the schema to load
        schema_dir: Optional directory containing schemas
        
    Returns:
        Loaded schema dictionary
        
    Raises:
        FileNotFoundError: If schema file doesn't exist
        json.JSONDecodeError: If schema file is invalid JSON
    """
    # Get schema path
    if schema_dir:
        schema_path = Path(schema_dir) / f"{schema_name}.json"
    else:
        schema_path = Path(__file__).parent / f"{schema_name}.json"
        
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_name}")
        
    # Load schema
    with open(schema_path) as f:
        return json.load(f)

def validate(
    data: Dict[str, Any],
    schema_name: str,
    schema_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validate data against a JSON schema.
    
    Args:
        data: Data to validate
        schema_name: Name of the schema to use
        schema_dir: Optional directory containing schemas
        
    Returns:
        Dictionary containing:
            - valid: Whether validation passed
            - errors: List of validation errors
    """
    try:
        # Load schema
        schema = load_schema(schema_name, schema_dir)
            
        # Validate
        jsonschema_validate(instance=data, schema=schema)
        
        return {
            "valid": True,
            "errors": []
        }
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return {
            "valid": False,
            "errors": [str(e)]
        }
        
    except Exception as e:
        logger.error(f"Error during validation: {e}")
        return {
            "valid": False,
            "errors": [str(e)]
        }

def validate_multiple(
    data_list: List[Dict[str, Any]],
    schema_name: str,
    schema_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validate multiple data items against a schema.
    
    Args:
        data_list: List of data items to validate
        schema_name: Name of the schema to use
        schema_dir: Optional directory containing schemas
        
    Returns:
        Dictionary containing:
            - valid: Whether all validations passed
            - errors: List of validation errors by index
    """
    results = []
    all_valid = True
    
    for i, data in enumerate(data_list):
        result = validate(data, schema_name, schema_dir)
        if not result["valid"]:
            all_valid = False
            results.append({
                "index": i,
                "errors": result["errors"]
            })
    
    return {
        "valid": all_valid,
        "errors": results
    }

def create_schema(
    schema_name: str,
    schema_data: Dict[str, Any],
    schema_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new JSON schema.
    
    Args:
        schema_name: Name for the schema
        schema_data: Schema definition
        schema_dir: Optional directory to save schema
        
    Returns:
        Dictionary containing:
            - success: Whether schema was created
            - error: Error message if failed
    """
    try:
        # Determine schema path
        if schema_dir:
            schema_dir = Path(schema_dir)
        else:
            schema_dir = Path(__file__).parent / "schemas"
            
        schema_dir.mkdir(parents=True, exist_ok=True)
        schema_path = schema_dir / f"{schema_name}.json"
        
        # Don't overwrite existing schema
        if schema_path.exists():
            return {
                "success": False,
                "error": f"Schema already exists: {schema_name}"
            }
            
        # Save schema
        with open(schema_path, 'w') as f:
            json.dump(schema_data, f, indent=2)
            
        return {
            "success": True,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Error creating schema: {e}")
        return {
            "success": False,
            "error": str(e)
        }

__all__ = ['validate', 'validate_multiple', 'create_schema', 'load_schema']
