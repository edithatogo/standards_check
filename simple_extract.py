import os

# Simple script to list DOCX files and create a basic extraction plan
print("Checking for DOCX files...")

docx_dir = "docx/variants"
if os.path.exists(docx_dir):
    print(f"Directory {docx_dir} exists")
    files = os.listdir(docx_dir)
    docx_files = [f for f in files if f.endswith('.docx')]
    print(f"Found {len(docx_files)} DOCX files:")
    for f in docx_files:
        print(f"  - {f}")
    
    # Create a simple plan file
    with open("extraction_plan.txt", "w") as plan_file:
        plan_file.write("DOCX Extraction Plan\n")
        plan_file.write("===================\n\n")
        plan_file.write("Files to process:\n")
        for f in docx_files:
            plan_file.write(f"- {f}\n")
    
    print("Created extraction_plan.txt")
else:
    print(f"Directory {docx_dir} does not exist")