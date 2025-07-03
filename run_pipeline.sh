#!/bin/bash
input_file="wiki_data.txt"
while IFS= read -r line; do
    term=$(echo "$line" | sed -E 's/[^[:alnum:]_]+/ /g') # Replace with a term if needed.
    if [[ -n "$term" ]]; then
        echo "Running: python3 wiki_scrapper.py \"$term\""
        python3 wiki_scrapper.py "$term"
    fi
done < "$input_file"