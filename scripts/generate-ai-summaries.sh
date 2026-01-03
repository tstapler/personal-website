#!/bin/bash
# AI Summary Build Integration for Hugo

echo "🤖 Starting AI summary generation process..."

# Check if AI summary requirements are installed
python3 -c "import aiohttp" 2>/dev/null || {
    echo "❌ Installing aiohttp for AI summaries..."
    pip install --user aiohttp
}

echo "📝 Processing blog posts for AI summaries..."

# Find all markdown files in content directory
find content/blog -name "*.md" -not -path "*/test-summaries/*" | while read file; do
    echo "Processing: $file"
    
    # Generate summary
    summary=$(python3 scripts/ai_summary_generator.py --file "$file" 2>/dev/null | head -n 1)
    
    if [ -n "$summary" ]; then
        echo "✅ Summary generated: ${summary:0:50]}..."
        
        # Add summary to frontmatter if not present
        if ! grep -q "^summary:" "$file"; then
            # Find the line after frontmatter ends
            end_line=$(grep -n "^+++" "$file" | tail -n 1 | cut -d: -f1)
            if [ -z "$end_line" ]; then
                end_line=1
            fi
            
            # Insert summary after frontmatter
            sed -i "${end_line}a\\nsummary = \"$summary\"" "$file"
            echo "📝 Added summary to $file"
        else
            echo "ℹ️  Summary already exists in $file"
        fi
    else
        echo "❌ Failed to generate summary for $file"
    fi
done

echo "✅ AI summary generation complete"
