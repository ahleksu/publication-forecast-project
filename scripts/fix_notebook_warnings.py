"""Script to fix FutureWarning messages in the HEI Executive Report notebook.

This script:
1. Adds observed=False to all pivot_table calls
2. Clears stderr outputs containing FutureWarning messages
"""
import json
from pathlib import Path

def fix_notebook():
    notebook_path = Path(__file__).parent.parent / "reports" / "HEI_Executive_Report.ipynb"
    
    # Read notebook
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    changes_made = 0
    
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            # Fix source: add observed=False to pivot_table calls that don't have it
            source_lines = cell["source"]
            new_source = []
            for i, line in enumerate(source_lines):
                if "pivot_table(" in line and "observed" not in "".join(source_lines[max(0,i-5):i+5]):
                    # Check if this is the start of a pivot_table call
                    pass
                new_source.append(line)
            
            # Join and replace - more reliable approach
            source_str = "".join(source_lines)
            
            # Add observed=False to pivot_table calls that don't have it
            if ".pivot_table(\n" in source_str and "observed=False" not in source_str:
                source_str = source_str.replace(
                    "    aggfunc='sum'\n)",
                    "    aggfunc='sum',\n    observed=False\n)"
                )
                source_str = source_str.replace(
                    "    aggfunc='first'\n    )",
                    "    aggfunc='first',\n    observed=False\n    )"
                )
                cell["source"] = source_str.split("\n")
                cell["source"] = [line + "\n" if i < len(cell["source"]) - 1 else line 
                                  for i, line in enumerate(source_str.split("\n"))]
                changes_made += 1
            
            # Clear stderr outputs containing FutureWarning
            if "outputs" in cell:
                new_outputs = []
                for output in cell["outputs"]:
                    if output.get("name") == "stderr":
                        text = "".join(output.get("text", []))
                        if "FutureWarning" in text:
                            changes_made += 1
                            continue  # Skip this warning output
                    new_outputs.append(output)
                cell["outputs"] = new_outputs
    
    # Write back
    with open(notebook_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=4)
    
    print(f"✅ Fixed {changes_made} issues in {notebook_path.name}")
    return changes_made

if __name__ == "__main__":
    fix_notebook()
