#!/bin/bash

# Check if the DOCX file exists
if [ -f "docx/variants/consort-cluster-crossover.docx" ]; then
    echo "File exists"
    ls -la docx/variants/consort-cluster-crossover.docx
    
    # Try to extract content using pandoc
    echo "Attempting to extract content using pandoc..."
    pandoc -f docx -t markdown docx/variants/consort-cluster-crossover.docx > consort-cluster-crossover-content.md
    echo "Content extraction complete"
    
    # Check if the output file was created
    if [ -f "consort-cluster-crossover-content.md" ]; then
        echo "Content extracted to consort-cluster-crossover-content.md"
        head -20 consort-cluster-crossover-content.md
    else
        echo "Failed to create output file"
    fi
else
    echo "File does not exist"
    ls -la docx/variants/
fi