#!/bin/bash
# AI Summary Integration Script for Hugo
# Processes existing blog posts and adds AI-generated summaries

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTENT_DIR="content/blog"
PROVIDER="openai"  # Can be overridden with --provider
STYLE="concise"     # Can be overridden with --style
MAX_LENGTH=150      # Can be overridden with --max-length
BATCH_MODE=false
DRY_RUN=false

# Help function
show_help() {
    cat << EOF
AI Summary Integration for Hugo Blog Posts

Usage: $0 [OPTIONS] [FILES...]

OPTIONS:
    -p, --provider PROVIDER    AI provider to use (openai, local) [default: openai]
    -s, --style STYLE        Summary style: concise, detailed, academic [default: concise]
    -l, --max-length NUM     Maximum summary length in words [default: 150]
    -b, --batch             Process all markdown files in content/blog/
    -d, --dry-run           Show what would be processed without making changes
    -h, --help              Show this help message

EXAMPLES:
    $0 --provider openai --style detailed content/blog/post.md
    $0 --batch --provider local content/blog/*.md
    $0 --dry-run --batch content/blog/*.md

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--provider)
            PROVIDER="$2"
            shift 2
            ;;
        -s|--style)
            STYLE="$2"
            shift 2
            ;;
        -l|--max-length)
            MAX_LENGTH="$2"
            shift 2
            ;;
        -b|--batch)
            BATCH_MODE=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
        *)
            break
            ;;
    esac
    shift
done

# Initialize counters
PROCESSED=0
UPDATED=0
ERRORS=0

echo "🤖 Starting AI summary integration..."
echo "Provider: $PROVIDER | Style: $STYLE | Max Length: $MAX_LENGTH words"
echo ""

# Function to process a single file
process_file() {
    local file="$1"
    local filename=$(basename "$file")
    
    echo "📝 Processing: $filename"
    
    # Check if file exists and is markdown
    if [[ ! -f "$file" || ! "$file" =~ \.md$ ]]; then
        echo "❌ Skipped: Not a markdown file or doesn't exist"
        ((ERRORS++))
        return
    fi
    
    # Skip if already has AI summary (unless dry run)
    if [[ "$DRY_RUN" != "true" ]]; then
        if grep -q "^ai_summary:" "$file"; then
            echo "ℹ️  Skipped: Already has AI summary"
            return
        fi
    fi
    
    # Extract content after frontmatter
    local temp_content=$(mktemp)
    sed -n '/^---$/,/^---$/!p' "$file" > "$temp_content"
    local content=$(cat "$temp_content")
    rm "$temp_content"
    
    if [[ -z "$content" ]]; then
        echo "⚠️  Skipped: No content to summarize"
        return
    fi
    
    # Generate AI summary
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "[DRY RUN] Would generate summary for: $filename"
        ((PROCESSED++))
        return
    fi
    
    local summary
    summary=$(python3 "$SCRIPT_DIR/ai_summary_generator.py" \
        --content "$content" \
        --provider "$PROVIDER" \
        --style "$STYLE" \
        --max-length "$MAX_LENGTH" 2>/dev/null)
    
    if [[ $? -eq 0 && -n "$summary" ]]; then
        # Create backup
        cp "$file" "$file.backup"
        
        # Add AI summary fields to frontmatter
        local temp_frontmatter=$(mktemp)
        sed -n '/^---$/,/^---$/p' "$file" > "$temp_frontmatter"
        
        # Build new frontmatter with AI fields
        {
            echo "---"
            cat "$temp_frontmatter"
            echo "ai_summary: \"$summary\""
            echo "ai_summary_provider: \"$PROVIDER\""
            echo "ai_summary_style: \"$STYLE\""
            echo "ai_summary_length: $(echo "$summary" | wc -w)"
            echo "ai_generated: true"
            echo "---"
        } > "$temp_new"
        
        # Combine with content
        cat "$temp_new" > "$file.tmp"
        sed -n '/^---$/,/^---$/!p' "$file" >> "$file.tmp"
        mv "$file.tmp" "$file"
        
        # Cleanup
        rm -f "$temp_frontmatter" "$temp_new"
        
        echo "✅ Updated: $filename (AI summary: ${summary:0:30]}...)"
        ((UPDATED++))
    else
        echo "❌ Failed to generate summary for: $filename"
        ((ERRORS++))
    fi
    
    ((PROCESSED++))
}

# Main processing logic
if [[ "$BATCH_MODE" == "true" ]]; then
    echo "🔄 Batch mode: processing all markdown files in $CONTENT_DIR"
    
    # Find all markdown files
    for file in "$CONTENT_DIR"/*.md; do
        if [[ -f "$file" ]]; then
            process_file "$file"
        fi
    done
else
    # Process specific files
    if [[ $# -eq 0 ]]; then
        echo "❌ No files specified. Use --help for usage information."
        exit 1
    fi
    
    for file in "$@"; do
        if [[ -f "$file" ]]; then
            process_file "$file"
        fi
    done
fi

# Summary
echo ""
echo "📊 Summary Results:"
echo "  Processed: $PROCESSED files"
echo "  Updated:   $UPDATED files"
echo "  Errors:    $ERRORS files"

if [[ $ERRORS -gt 0 ]]; then
    echo "❌ Some files had errors. Check the output above."
    exit 1
elif [[ $UPDATED -gt 0 ]]; then
    echo "✅ Successfully added AI summaries to $UPDATED files."
    exit 0
else
    echo "ℹ️  No files required updates."
    exit 0
fi