import time
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM


def truncate_to_last_sentence(text):
    last_period = text.rfind(".")
    if last_period != -1:
        return text[:last_period + 1]
    return text


def generate_response(query, context, model_path):
    """
    Genera una respuesta usando el modelo fine-tuned.
    Retorna (response, inference_time).
    """
    try:
        # Inicializar modelo y tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(model_path)
        text_gen_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)

        prompt = (
            f"Pregunta: {query}\n"
            f"Contexto: {context}\n\n"
            "Respuesta:"
        )

        start_time = time.time()

        result = text_gen_pipeline(prompt, max_new_tokens=150, do_sample=True, temperature=0.4)
        raw_response = result[0]["generated_text"]

        end_time = time.time()
        inference_time = end_time - start_time

        if "Respuesta:" in raw_response:
            response = raw_response.split("Respuesta:")[-1].strip()
        else:
            response = raw_response.strip()

        response = truncate_to_last_sentence(response)
        return response, inference_time

    except Exception as e:
        print(f"Error generando la respuesta: {str(e)}")
        raise
