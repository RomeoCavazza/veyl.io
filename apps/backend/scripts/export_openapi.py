import sys
import json
import os

# Add the parent directory to sys.path to allow importing app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

def export_openapi():
    openapi_data = app.openapi()
    
    # Output to stdout or file
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
        with open(output_path, "w") as f:
            json.dump(openapi_data, f, indent=2)
        print(f"OpenAPI schema exported to {output_path}")
    else:
        print(json.dumps(openapi_data, indent=2))

if __name__ == "__main__":
    export_openapi()
