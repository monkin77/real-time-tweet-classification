'''
This file contains the model and tokenizer for the DistilBERT text classification task.
'''
import keras
import keras_nlp


'''
Use a shorter sequence length. Sequence length is the maximum length of input sequences.
We saw above that the maximum length of a training sample is 157 characters. Thus, we can set the sequence length to 160.
'''
preprocessor = keras_nlp.models.DistilBertPreprocessor.from_preset(
    preset,                         # Label of DistilBERT model preset
    sequence_length=160,            # Shorter sequence length for faster training. Sequence length is the maximum length of input sequences.
    name="preprocessor_4_tweets"    # Name of the preprocessor layer
)


# Load Classifier model.
trained_model_path = "trained_model.keras"
classifier: keras_nlp.models.Classifier = keras.models.load_model(trained_model_path)
