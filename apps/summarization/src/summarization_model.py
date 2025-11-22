from transformers import AutoTokenizer, T5ForConditionalGeneration


class SummarizationModel:
    def __init__(self, model_name='IlyaGusev/rut5_base_sum_gazeta'):
        self.model_name = model_name
        self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        self._model = T5ForConditionalGeneration.from_pretrained(model_name)

    def summarize(self, text):
        input_ids = self._tokenizer(
            [text],
            max_length=1024,
            padding='max_length',
            truncation=True,
            return_tensors='pt',
        )['input_ids']
        output_ids = self._model.generate(
            input_ids=input_ids,
            no_repeat_ngram_size=4,
            num_beams=5,
        )[0]
        summary = self._tokenizer.decode(
            output_ids,
            skip_special_tokens=True
        )

        return summary