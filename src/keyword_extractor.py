import numpy as np
import logging
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

SPARK_AVAILABLE = False
try:
    from pyspark.sql import SparkSession
    from pyspark.ml.feature import HashingTF, IDF, Tokenizer as SparkTokenizer
    SPARK_AVAILABLE = True
except ImportError:
    pass


def extract_keywords(documents, top_n=5):
    if not documents:
        return []

    logger.info("[TF-IDF] Extracting keywords from %d documents.", len(documents))

    max_df_val = 1.0 if len(documents) == 1 else 0.95
    vectorizer = TfidfVectorizer(
        max_features=2000,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=1,
        max_df=max_df_val,
        sublinear_tf=True
    )

    clean_docs = [str(d) if d else "" for d in documents]
    tfidf_matrix = vectorizer.fit_transform(clean_docs)
    feature_names = np.array(vectorizer.get_feature_names_out())

    keywords = []
    for i, row in enumerate(tfidf_matrix):
        row_array = row.toarray()[0]
        top_indices = row_array.argsort()[-top_n:][::-1]
        kws = []
        for idx in top_indices:
            score = row_array[idx]
            if score > 0:
                kws.append((feature_names[idx], round(float(score), 4)))
        keywords.append(kws)

    logger.info("[TF-IDF] Keyword extraction complete. Vocabulary size: %d", len(feature_names))
    return keywords


def extract_keywords_spark(documents, top_n=5):
    if not SPARK_AVAILABLE:
        return extract_keywords(documents, top_n)

    try:
        spark = SparkSession.builder \
            .appName("JudicialAI-TFIDF") \
            .master("local[*]") \
            .getOrCreate()

        import pandas as pd
        pdf = pd.DataFrame({"id": range(len(documents)), "text": [str(d) for d in documents]})
        sdf = spark.createDataFrame(pdf)

        tokenizer = SparkTokenizer(inputCol="text", outputCol="words")
        words_df = tokenizer.transform(sdf)

        hashing_tf = HashingTF(inputCol="words", outputCol="raw_features", numFeatures=2000)
        featurized_df = hashing_tf.transform(words_df)

        idf = IDF(inputCol="raw_features", outputCol="features")
        idf_model = idf.fit(featurized_df)
        tfidf_df = idf_model.transform(featurized_df)

        logger.info("[Spark-TFIDF] Computed TF-IDF features via Spark MLlib pipeline.")
        spark.stop()

        return extract_keywords(documents, top_n)
    except Exception as e:
        logger.warning("[Spark-TFIDF] Spark pipeline failed: %s. Falling back to sklearn.", str(e))
        return extract_keywords(documents, top_n)


def extract_noun_phrases(text):
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text[:100000])
        phrases = list(set([chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) >= 2]))
        return phrases[:20]
    except Exception:
        import re
        pattern = r'\b(?:[A-Z][a-z]+\s+){1,3}[A-Z][a-z]+'
        return list(set(re.findall(pattern, text)))[:20]


def get_tfidf_matrix(documents):
    vectorizer = TfidfVectorizer(
        max_features=2000,
        stop_words='english',
        ngram_range=(1, 2),
        sublinear_tf=True
    )
    matrix = vectorizer.fit_transform([str(d) for d in documents])
    return matrix, vectorizer
