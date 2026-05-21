import torch
from transformers import Pipeline

# We inherit directly from the official Hugging Face Pipeline base class.
# This ensures it uses their rigorous streaming, hardware mapping, and batching.
class AlgorithmicSummaryPipeline(Pipeline):
    
    def _sanitize_parameters(self, **kwargs):
        # Maps incoming user style flags cleanly to the underlying forward pass
        preprocess_kwargs = {}
        forward_kwargs = {}
        postprocess_kwargs = {}
        
        # Pull out generation parameters for the model filter
        for key in ["max_new_tokens", "min_new_tokens", "length_penalty", 
                    "repetition_penalty", "no_repeat_ngram_size", "do_sample", "temperature"]:
            if key in kwargs:
                forward_kwargs[key] = kwargs[key]
                
        return preprocess_kwargs, forward_kwargs, postprocess_kwargs

    def preprocess(self, text, **preprocess_kwargs):
        # FILTER 1: Raw text -> Token Tensor Dictionary
        # T5 requires the task prefix string prepended
        model_inputs = self.tokenizer(
            "summarize: " + text, 
            max_length=1000, 
            truncation=True, 
            return_tensors="pt"
        )
        return model_inputs

    def _forward(self, model_inputs, **forward_kwargs):
        # FILTER 2: Hardware-Accelerated Inference Pass
        # We extract target variables out of the input dictionary
        input_ids = model_inputs["input_ids"]
        attention_mask = model_inputs["attention_mask"]
        
        # Run generation loop under explicit inference memory isolation
        with torch.inference_mode():
            outputs = self.model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                **forward_kwargs
            )
        return outputs

    def postprocess(self, model_outputs, **postprocess_kwargs):
        # FILTER 3: Vector Tensors -> Clean Output String
        decoded_string = self.tokenizer.decode(model_outputs[0], skip_special_tokens=True)
        return decoded_string.strip()
