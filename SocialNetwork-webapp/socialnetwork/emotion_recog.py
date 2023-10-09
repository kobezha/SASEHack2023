import numpy as np
import pandas as pd
import pickle

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Dense, LSTM, Embedding, Bidirectional

from keras.models import load_model

# Trains a emotion recognition model to classify text with its most likely emotion 
# sadness, anger, love, surprise, fear, joy
# Referenced https://www.kaggle.com/code/zeyadkhalid/emotion-recognition-lstm-93-accuracy


# Emotions dataset for NLP:
# https://www.kaggle.com/datasets/praveengovi/emotions-dataset-for-nlp

# Pretrained GLOVE embeddings used:
# https://www.kaggle.com/datasets/rtatman/glove-global-vectors-for-word-representation

#### Preprocessing

import re
import string
str_punc = string.punctuation.replace(',', '').replace("'",'')

def clean(text):
    global str_punc
    text = re.sub(r'[^a-zA-Z ]', '', text)
    text = text.lower()
    return text  

def train_model():
    ####### Load datasets
    train_path = "../../emotions-dataset/train.txt"
    val_path = "../../emotions-dataset/val.txt"
    test_path = "../../emotions-dataset/test.txt"
    df_train = pd.read_csv(train_path, names=['Text', 'Emotion'], sep=';')
    X_train, y_train = df_train['Text'].apply(clean), df_train['Emotion']

    df_val = pd.read_csv(val_path, names=['Text', 'Emotion'], sep=';')
    X_val, y_val = df_val['Text'].apply(clean), df_val['Emotion']

    df_test = pd.read_csv(test_path, names=['Text', 'Emotion'], sep=';')
    X_test, y_test = df_test['Text'].apply(clean), df_test['Emotion']

    

    ####### encode the emotion labels (ex. anger, sadness)
    le = LabelEncoder()

    # get encoded lables
    y_train = le.fit_transform(y_train)
    # apply this same mapping to test and val
    y_test = le.transform(y_test)
    y_val = le.transform(y_val)

    # after encoding labels as integers, convert them to one-hot vectors
    y_train = to_categorical(y_train)
    y_test = to_categorical(y_test)
    y_val = to_categorical(y_val)

    ##### TOKENIZING TEXT DATA
    # Tokenize and pad sequences so that it can be used in neural network

    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(pd.concat([X_train, X_test], axis=0))

    sequences_train = tokenizer.texts_to_sequences(X_train)
    sequences_test = tokenizer.texts_to_sequences(X_test)
    sequences_val = tokenizer.texts_to_sequences(X_val)

    # ensure all sequences have the same length
    X_train = pad_sequences(sequences_train, maxlen=256, truncating='pre')
    X_test = pad_sequences(sequences_test, maxlen=256, truncating='pre')
    X_val = pad_sequences(sequences_val, maxlen=256, truncating='pre')

    vocabSize = len(tokenizer.index_word) + 1

    # save tokenizer and label encoder
    with open('tokenizer.pickle', 'wb') as f:
        pickle.dump(tokenizer, f)
        
    with open('labelEncoder.pickle', 'wb') as f:
        pickle.dump(le, f)


    ##### USE PRETRAINED GLOVE EMBEDDINGS
    """
    WDTM? -- GloVe embeddings have been widely used in NLP
    considered to be a powerful way to represent words in a more semantically meaningful manner 
    compared to traditional methods like one-hot encoding or TF-IDF
    """
    path_to_glove_file = '../../glove-dataset/glove.6B.200d.txt'
    num_tokens = 16185
    embedding_dim = 200
    hits = 0
    misses = 0
    embeddings_index = {}

    # Read word vectors
    with open(path_to_glove_file) as f:
        for line in f:
            
            word, coefs = line.split(maxsplit=1)
            # coefs = np.fromstring(coefs, "f", sep=" ")
            
            coefs = coefs.split()
            coefs = np.array(coefs, dtype=np.float32)
            
            embeddings_index[word] = coefs
    print("Found %s word vectors." % len(embeddings_index))

    # Assign word vectors to our dictionary/vocabulary
    embedding_matrix = np.zeros((num_tokens, embedding_dim))
    for word, i in tokenizer.word_index.items():
        embedding_vector = embeddings_index.get(word)
        
        if embedding_vector is not None:
            
            # Words not found in embedding index will be all-zeros.
            # This includes the representation for "padding" and "OOV"
            embedding_matrix[i] = embedding_vector
            hits += 1
        else:
            misses += 1
    print("Converted %d words (%d misses)" % (hits, misses))




    ######## specify neural network parameters
    adam = Adam(learning_rate=0.005)

    model = Sequential()
    model.add(Embedding(vocabSize, 200, input_length=X_train.shape[1], weights=[embedding_matrix], trainable=False))
    model.add(Bidirectional(LSTM(256, dropout=0.2,recurrent_dropout=0.2, return_sequences=True)))
    model.add(Bidirectional(LSTM(128, dropout=0.2,recurrent_dropout=0.2, return_sequences=True)))
    model.add(Bidirectional(LSTM(128, dropout=0.2,recurrent_dropout=0.2)))
    model.add(Dense(6, activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer=adam, metrics=['accuracy'])
    callback = EarlyStopping(
        monitor="val_loss",
        patience=2,
        restore_best_weights=True,
    )

    # Fit model
    history = model.fit(X_train,
                        y_train,
                        validation_data=(X_test, y_test),
                        verbose=1,
                        batch_size=256,
                        epochs=10,
                        callbacks=[callback]
                    )


    model.save('emotion-recog-model.h5')

def classify_emotion(text):
    # load label encoder
    le_path = "socialnetwork/labelEncoder.pickle"
    with open(le_path, "rb") as f:
        # Use the pickle.load() function to deserialize the data
        le = pickle.load(f)

    # load tokenizer
    tokenizer_path = "socialnetwork/tokenizer.pickle"
    with open(tokenizer_path, "rb") as f:
        # Use the pickle.load() function to deserialize the data
        tokenizer = pickle.load(f)

    # load saved trained emotion recog model
    model_path = "socialnetwork/emotion-recog-model.h5"
    model = load_model(model_path)


    # check model output on these sentences
    sentence = text
    
    sentence = clean(sentence)
    sentence = tokenizer.texts_to_sequences([sentence])
    sentence = pad_sequences(sentence, maxlen=256, truncating='pre')
    result = le.inverse_transform(np.argmax(model.predict(sentence, verbose=0), axis=-1))[0]
    proba =  np.max(model.predict(sentence, verbose=0))
    return result
    
    
    # bigger model evaluation (on test data) --> has 92.4% accuracy
    """
    test_path = "../../emotions-dataset/test.txt"
    
    df_test = pd.read_csv(test_path, names=['Text', 'Emotion'], sep=';')
    X_test, y_test = df_test['Text'].apply(clean), df_test['Emotion']
    sequences_test = tokenizer.texts_to_sequences(X_test)
    X_test = pad_sequences(sequences_test, maxlen=256, truncating='pre')

    y_test = le.transform(y_test)
    y_test = to_categorical(y_test)
    model.evaluate(X_test, y_test, verbose=1)
    """
   
def main():

    
    # testing classify_emotion()
    # sadness examples
    print(classify_emotion("im feeling rather bad because school is so stressful right now"))
    print(classify_emotion("im feeling really emotional right now"))
    print(classify_emotion("i realized my mistake and i m really feeling terrible and thinking that i shouldnt have done that"))
    print(classify_emotion("i journaled about my tendency to sometimes overcommit myself which can make me feel exhausted and overwhelmed"))

    # joy examples
    print(classify_emotion("I feel reassured that i am dealing with my diet in the right way and that all is good :)"))
    print(classify_emotion("i am feeling so happy these days"))
    print(classify_emotion("i feel as though ive reached a point in my career where im highly respected there"))

    # anger examples
    print(classify_emotion("i just plain feel envious of the self confidence she has"))
    



if __name__ == "__main__":
    main()


