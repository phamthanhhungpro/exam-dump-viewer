#!/usr/bin/env python3
"""
PDF Parser for AWS SAP-C02 Exam Questions
Parses PDF files containing exam questions and converts them to JSON format.

This parser is specifically designed for ExamTopics format PDFs and outputs
questions in the requested JSON format with proper answer indexing.

Output format:
{
  "question": "Question text here...",
  "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
  "answer": 2,  // Index of correct answer (0=A, 1=B, 2=C, 3=D) OR [1,3] for multiple choice
  "is_multiple_choice": false,  // true if question requires multiple answers
  "source": {
    "correct_answer": "C",
    "community_answer": "C", 
    "community_confidence": "high"
  }
}
"""

import pdfplumber
import re
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import warnings
import sys
import os

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
    is_multiple_choice = False
    
    current_option = None
    in_options = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for multiple choice indicators
        if (re.search(r'\(.*choose.*(two|three|2|3).*\)', line, re.I) or 
            re.search(r'\(.*choose.*(two|three|2|3).*\)', question_text, re.I)):
            is_multiple_choice = True
            
        # Check for correct answer - handle multiple answers
        answer_match = re.match(r'Correct\s+Answer:\s*([A-D,\s]+)', line, re.I)
        if answer_match:
            correct_answer = answer_match.group(1).upper().replace(' ', '').replace(',', '')
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
    community_match = re.search(r'Selected Answer:\s*([A-D,\s]+)', question_text, re.I)
    if community_match:
        community_answer = community_match.group(1).upper().replace(' ', '').replace(',', '')
    
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
        'community_confidence': community_confidence,
        'is_multiple_choice': is_multiple_choice
    }

def parse_pdf(pdf_path, max_pages=None):
    """Parse PDF and extract questions in the specified JSON format"""
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

    # Find all question blocks
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
                print(f"Skipping question {i+1}: Insufficient data")
                continue
            
            # Determine final answer (prefer community if available)
            final_answer = parsed['community_answer'] if parsed['community_answer'] else parsed['correct_answer']
            
            # Handle multiple choice questions
            if parsed['is_multiple_choice'] and len(final_answer) > 1:
                # Convert multiple letters to array of indices
                answer_indices = [ord(letter) - ord('A') for letter in final_answer if letter.isalpha()]
                
                # Validate all answer indices
                valid_indices = [idx for idx in answer_indices if 0 <= idx < len(parsed['options'])]
                if len(valid_indices) != len(answer_indices) or len(valid_indices) == 0:
                    print(f"Skipping question {i+1}: Some answer indices out of range")
                    continue
                    
                answer_value = valid_indices
            else:
                # Single choice question
                if not final_answer or len(final_answer) == 0:
                    print(f"Skipping question {i+1}: No answer found")
                    continue
                    
                # Take the first letter for single choice
                first_letter = final_answer[0] if final_answer[0].isalpha() else None
                if not first_letter:
                    print(f"Skipping question {i+1}: Invalid answer format")
                    continue
                    
                answer_index = ord(first_letter) - ord('A')
                
                # Validate answer index
                if not (0 <= answer_index < len(parsed['options'])):
                    print(f"Skipping question {i+1}: Answer index out of range")
                    continue
                    
                answer_value = answer_index
            
            question_data = {
                "question": parsed['question'],
                "options": parsed['options'],
                "answer": answer_value,
                "is_multiple_choice": parsed['is_multiple_choice'],
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

def choose_file():
    """GUI file chooser for selecting PDF file"""
    file_path = filedialog.askopenfilename(
        title="Choose PDF file to parse",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if not file_path:
        return

    try:
        data = parse_pdf(file_path)
        output_path = file_path.replace(".pdf", "_parsed.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        messagebox.showinfo(
            "Success",
            f"Parsed {len(data)} questions from PDF.\nJSON file saved at:\n{output_path}"
        )
    except Exception as e:
        messagebox.showerror("Error", str(e))

def main():
    """Main function - can be used as GUI or command line"""
    if len(sys.argv) > 1:
        # Command line mode
        pdf_file = sys.argv[1]
        max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else None
        
        if not os.path.exists(pdf_file):
            print(f"Error: File '{pdf_file}' not found")
            sys.exit(1)
        
        try:
            questions = parse_pdf(pdf_file, max_pages)
            
            # Generate output filename
            base_name = os.path.splitext(pdf_file)[0]
            suffix = f"_first_{max_pages}_pages" if max_pages else "_full"
            output_file = f"{base_name}{suffix}.json"
            
            # Save to JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(questions, f, indent=2, ensure_ascii=False)
            
            print(f"\nSuccess!")
            print(f"Extracted {len(questions)} questions")
            print(f"Output saved to: {output_file}")
            
            # Show sample question
            if questions:
                print(f"\nSample question:")
                sample = questions[0]
                print(f"Question: {sample['question'][:100]}...")
                print(f"Options ({len(sample['options'])}):")
                
                if sample['is_multiple_choice']:
                    # Multiple choice - show all correct answers
                    for i, option in enumerate(sample['options']):
                        marker = "→" if i in sample['answer'] else " "
                        print(f"  {marker} {chr(ord('A') + i)}. {option[:80]}...")
                    correct_letters = [chr(ord('A') + idx) for idx in sample['answer']]
                    print(f"Answers: {sample['answer']} ({', '.join(correct_letters)}) - Multiple Choice")
                else:
                    # Single choice
                    for i, option in enumerate(sample['options']):
                        marker = "→" if i == sample['answer'] else " "
                        print(f"  {marker} {chr(ord('A') + i)}. {option[:80]}...")
                    print(f"Answer: {sample['answer']} ({chr(ord('A') + sample['answer'])})")
                    
                print(f"Source: {sample['source']}")
            
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        # GUI mode
        root = tk.Tk()
        root.withdraw()  # Hide main window
        choose_file()

if __name__ == "__main__":
    main()
