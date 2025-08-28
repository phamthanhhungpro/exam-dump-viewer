# PDF Parser for AWS SAP-C02 Exam Questions

This Python script parses PDF files containing AWS SAP-C02 exam questions (specifically from ExamTopics format) and converts them to structured JSON format.

## Features

- Parses ExamTopics PDF format
- Extracts questions, multiple choice options, and answers
- Supports both correct answers and community answers
- Includes community confidence levels
- Can process entire PDF or limit to specific number of pages
- Both GUI and command-line interfaces
- Outputs clean, structured JSON format

## Output Format

Each question is formatted as follows:

**Single Choice Questions:**
```json
{
  "question": "A company is hosting an image-processing service on AWS in a VPC...",
  "options": [
    "Replace the NAT gateways with NAT instances...",
    "Move the EC2 instances to the public subnets...",
    "Set up an S3 gateway VPC endpoint...",
    "Another option text..."
  ],
  "answer": 2,
  "is_multiple_choice": false,
  "source": {
    "correct_answer": "C",
    "community_answer": "C",
    "community_confidence": "high"
  }
}
```

**Multiple Choice Questions (Choose Two/Three):**
```json
{
  "question": "Which combination of steps should the solutions architect take? (Choose two.)",
  "options": [
    "First option...",
    "Second option...",
    "Third option...",
    "Fourth option..."
  ],
  "answer": [1, 3],
  "is_multiple_choice": true,
  "source": {
    "correct_answer": "BD",
    "community_answer": "BD",
    "community_confidence": "high"
  }
}
```

Where:
- `question`: The full question text
- `options`: Array of answer choices (A, B, C, D)
- `answer`: For single choice: Zero-based index (0=A, 1=B, 2=C, 3=D). For multiple choice: Array of indices [1,3] = B,D
- `is_multiple_choice`: Boolean indicating if question requires multiple answers
- `source.correct_answer`: Official correct answer from the PDF (e.g., "C" or "BD")
- `source.community_answer`: Community-voted answer (if available)
- `source.community_confidence`: "high" (>70%), "medium" (>50%), "low" (≤50%), or "none"

## Requirements

```bash
pip install pdfplumber tkinter
```

## Usage

### Command Line Interface

```bash
# Parse entire PDF
python parser_working.py path/to/exam.pdf

# Parse first 100 pages only
python parser_working.py path/to/exam.pdf 100

# Examples
python parser_working.py "../SAP-C02_Answer1.pdf"
python parser_working.py "../SAP-C02_Answer1.pdf" 50
```

### GUI Interface

```bash
# Launch GUI file picker
python parser_working.py
```

This will open a file dialog where you can select the PDF file to parse.

## Files in this Package

- `parser_working.py` - Main parser with both GUI and CLI interfaces
- `final_parser.py` - Command-line only version with detailed output
- `batch_parser.py` - Alternative implementation
- `enhanced_parser.py` - Enhanced version with better error handling
- `debug_parser.py` - Debug utility to examine PDF structure

## Example Usage

```bash
cd "c:\Users\admin\Downloads\SAP\script"

# Parse first 10 pages for testing
python parser_working.py "../SAP-C02_Answer1.pdf" 10

# Parse entire PDF (this may take a while for large files)
python parser_working.py "../SAP-C02_Answer1.pdf"
```

## Output Files

The script generates JSON files with the following naming convention:
- `filename_parsed.json` (GUI mode)
- `filename_first_N_pages.json` (CLI mode with page limit)
- `filename_full.json` (CLI mode, entire file)

## Sample Output

```json
[
  {
    "question": "Question #1 Topic 1 A company needs to architect a hybrid DNS solution...",
    "options": [
      "Associate the private hosted zone to all the VPCs. Create a Route 53 inbound resolver...",
      "Associate the private hosted zone to all the VPCs. Deploy an Amazon EC2 conditional forwarder...",
      "Associate the private hosted zone to the shared services VPC. Create a Route 53 outbound resolver...",
      "Associate the private hosted zone to the shared services VPC. Create a Route 53 inbound resolver..."
    ],
    "answer": 0,
    "source": {
      "correct_answer": "D",
      "community_answer": "A",
      "community_confidence": "high"
    }
  }
]
```

## Features

### Answer Priority
- Community answers are preferred over official answers when available
- Community confidence is calculated based on vote percentages
- Falls back to official answer if no community vote exists

### Error Handling
- Skips questions with insufficient data
- Validates answer indices against available options
- Continues processing even if individual questions fail
- Provides detailed progress feedback

### Performance
- Processes large PDFs efficiently
- Shows progress updates every 50 pages
- Memory-efficient text processing
- Can limit processing to specific page ranges for testing

## Troubleshooting

### Common Issues

1. **PDF warnings**: The script suppresses common PDF parsing warnings, but functionality is not affected.

2. **No questions found**: Ensure the PDF is in ExamTopics format with "Question #N Topic N" headers.

3. **Invalid answer indices**: The script validates that answer indices match available options and skips invalid questions.

4. **Memory issues**: For very large PDFs, consider processing in smaller chunks using the page limit parameter.

### Debug Mode

Use `debug_parser.py` to examine the structure of your PDF:

```bash
python debug_parser.py
```

This will show you the raw text structure of the first few questions to help troubleshoot parsing issues.

## License

This script is provided as-is for educational purposes. Please ensure you have the right to parse and use the content from your PDF files.
