from transformers import pipeline
import os


def get_model_path():
    """Retrieves the model path """
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "LaMini-Flan-T5-248M")

def chunk_text(text, max_tokens=512):
    """Splits the input text into chunks of a maximum size (in tokens)."""
    sentences = text.split('. ')
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence.split())          #split into words 
        if current_length + sentence_length <= max_tokens:
            current_chunk.append(sentence)
            current_length += sentence_length
        else:
            chunks.append(". ".join(current_chunk) + ".")  
            current_chunk = [sentence]
            current_length = sentence_length

    if current_chunk:
        chunks.append(". ".join(current_chunk) + ".")
    return chunks

def summarize_chunk(summarizer, chunk, max_length=200, min_length=100):
    """Summarizes a chunk of text using the summarizer pipeline."""
    try:
        summary = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print(f"Error during summarization: {e}")
        return ""

def combine_summaries(summarized_chunks):
    combined_summary = " ".join(summarized_chunks)
    bullet_points = "\n".join(f"• {point.strip()}" for point in combined_summary.split('. ') if point)
    return bullet_points

def summarize_text(text):
    """Main function to summarize the input text."""
    print("Summarizing text...")

    model_path = get_model_path()
    summarizer = pipeline("summarization", model=model_path)
    chunks = chunk_text(text)
    summarized_chunks = [summarize_chunk(summarizer, chunk) for chunk in chunks]
    bullet_points = combine_summaries(summarized_chunks)
    return bullet_points
