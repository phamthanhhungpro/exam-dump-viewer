#!/usr/bin/env python3
"""
Final PDF Parser for AWS SAP-C02 Exam Questions
Based on actual ExamTopics structure analysis
"""

import pdfplumber
import re
import json
import sys
import os
import warnings

# Suppress PDF warnings
warnings.filterwarnings("ignore", category=UserWarning)

def clean_text(text):
    """Clean and normalize text"""
    # Remove excessive whitespace but preserve single spaces
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove common artifacts
    text = re.sub(r'6/8/24.*?ExamTopics', '', text)
    text = re.sub(r'https://www\.examtopics\.com.*?/', '', text)
    return text

def parse_question_from_text(question_text):
    """Parse a single question from raw text"""
    lines = question_text.split('\n')
    
    # Extract question content (everything before options)
    question_lines = []
    options = []
    correct_answer = None
    community_answer = None
    community_confidence = "none"
    
    current_option = None
    in_options = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for correct answer
        answer_match = re.match(r'Correct\s+Answer:\s*([A-D])', line, re.I)
        if answer_match:
            correct_answer = answer_match.group(1).upper()
            break
            
        # Check for option start
        option_match = re.match(r'^([A-D])\.\s*(.*)', line)
        if option_match:
            # Save previous option if exists
            if current_option:
                options.append(current_option[1].strip())
            
            current_option = [option_match.group(1), option_match.group(2)]
            in_options = True
            
        elif in_options and current_option:
            # Continue current option
            current_option[1] += ' ' + line
            
        elif not in_options:
            # Part of question text
            question_lines.append(line)
    
    # Save last option
    if current_option:
        options.append(current_option[1].strip())
    
    # Extract community information from the full text
    community_match = re.search(r'Selected Answer:\s*([A-D])', question_text, re.I)
    if community_match:
        community_answer = community_match.group(1).upper()
    
    # Extract community vote distribution
    vote_matches = re.findall(r'([A-D])\s*\((\d+)%\)', question_text, re.I)
    if vote_matches:
        votes = {letter.upper(): int(percentage) for letter, percentage in vote_matches}
        max_vote = max(votes.values()) if votes else 0
        
        if max_vote > 70:
            community_confidence = "high"
        elif max_vote > 50:
            community_confidence = "medium"
        else:
            community_confidence = "low"
    
    # Clean up question text
    question = ' '.join(question_lines).strip()
    
    # Clean up options
    cleaned_options = []
    for option in options:
        # Remove excessive whitespace and normalize
        cleaned_option = re.sub(r'\s+', ' ', option.strip())
        if cleaned_option:
            cleaned_options.append(cleaned_option)
    
    return {
        'question': question,
        'options': cleaned_options,
        'correct_answer': correct_answer,
        'community_answer': community_answer,
        'community_confidence': community_confidence
    }

def parse_pdf_final(pdf_path, max_pages=None):
    """Final PDF parsing implementation"""
    print(f"Parsing PDF: {pdf_path}")
    
    all_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        pages_to_process = min(max_pages, total_pages) if max_pages else total_pages
        
        print(f"Processing {pages_to_process} of {total_pages} pages...")
        
        for i, page in enumerate(pdf.pages[:pages_to_process]):
            if page.extract_text():
                page_text = page.extract_text(x_tolerance=1, y_tolerance=1)
                all_text += page_text + "\n"
            
            if (i + 1) % 50 == 0:
                print(f"Processed {i + 1} pages...")

    # Find all question blocks using a more comprehensive approach
    question_pattern = r'Question\s*#\d+\s*Topic\s*\d+'
    question_matches = list(re.finditer(question_pattern, all_text, re.I))
    
    print(f"Found {len(question_matches)} question blocks")
    
    questions = []
    
    for i, match in enumerate(question_matches):
        try:
            # Get the text for this question
            start = match.start()
            
            # Find the end - either next question or end of text
            if i + 1 < len(question_matches):
                end = question_matches[i + 1].start()
            else:
                end = len(all_text)
            
            question_block = all_text[start:end]
            
            # Parse this question
            parsed = parse_question_from_text(question_block)
            
            # Validate the parsed question
            if (len(parsed['question']) < 30 or 
                len(parsed['options']) < 2 or 
                not parsed['correct_answer']):
                print(f"Skipping question {i+1}: Insufficient data (Q:{len(parsed['question'])}, O:{len(parsed['options'])}, A:{parsed['correct_answer']})")
                continue
            
            # Determine final answer (prefer community if available)
            final_answer = parsed['community_answer'] if parsed['community_answer'] else parsed['correct_answer']
            answer_index = ord(final_answer) - ord('A')
            
            # Validate answer index
            if not (0 <= answer_index < len(parsed['options'])):
                print(f"Skipping question {i+1}: Answer index {answer_index} out of range for {len(parsed['options'])} options")
                continue
            
            question_data = {
                "question": parsed['question'],
                "options": parsed['options'],
                "answer": answer_index,
                "source": {
                    "correct_answer": parsed['correct_answer'],
                    "community_answer": parsed['community_answer'],
                    "community_confidence": parsed['community_confidence']
                }
            }
            
            questions.append(question_data)
            
            if len(questions) % 10 == 0:
                print(f"Successfully parsed {len(questions)} questions...")
                
        except Exception as e:
            print(f"Error parsing question {i+1}: {e}")
            continue
    
    return questions

def main():
    if len(sys.argv) < 2:
        print("Usage: python final_parser.py <pdf_file> [max_pages]")
        print("Example: python final_parser.py SAP-C02_Answer1.pdf 100")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if not os.path.exists(pdf_file):
        print(f"Error: File '{pdf_file}' not found")
        sys.exit(1)
    
    try:
        # Parse the PDF
        questions = parse_pdf_final(pdf_file, max_pages)
        
        # Generate output filename
        base_name = os.path.splitext(pdf_file)[0]
        suffix = f"_first_{max_pages}_pages" if max_pages else "_full"
        output_file = f"{base_name}{suffix}_final.json"
        
        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
        
        print(f"\nSuccess!")
        print(f"Extracted {len(questions)} questions")
        print(f"Output saved to: {output_file}")
        
        # Show sample questions
        if questions:
            print(f"\n=== Sample Questions ===")
            for i, sample in enumerate(questions[:2]):
                print(f"\nQuestion {i+1}:")
                print(f"Q: {sample['question'][:150]}...")
                print(f"Options ({len(sample['options'])}):")
                for j, option in enumerate(sample['options']):
                    marker = "→" if j == sample['answer'] else " "
                    print(f"  {marker} {chr(ord('A') + j)}. {option[:100]}...")
                print(f"Answer: {sample['answer']} ({chr(ord('A') + sample['answer'])})")
                print(f"Source: {sample['source']}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
