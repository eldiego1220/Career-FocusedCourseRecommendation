import pandas as pd
import sqlalchemy as sa

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_matching_courses_for_jobs(
    jobs_df,
    courses_df,
    threshold=0.3,
    N=10,
    min_description_size=60,
    join_all_courses_cols=True,
    merge_sections=True,
):
    # First, ensure the data `nltk` needs to work is downloaded.
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)

    def tokenize_lemmatize_text(text):
        # First, we tokenize the text.
        word_tokens = word_tokenize(text.lower())
        # Then, we lemmatize the tokens and remove stopwords.
        stop_words = set(stopwords.words("english"))
        lemmatizer = WordNetLemmatizer()
        normalized_text = [
            lemmatizer.lemmatize(word) for word in word_tokens if word not in stop_words
        ]

        # Return space-separated, tokenized and lemmatized words.
        return " ".join(normalized_text)

    def tf_idf_vectorize(tokens, vocabulary=None):
        vectorizer = TfidfVectorizer(vocabulary=vocabulary)
        M = vectorizer.fit_transform(tokens)
        return M, vectorizer.vocabulary_

    # For matching, we'll consider only the job descriptions and course descriptions for now.
    #
    # We'll start by dropping all rows with NULL values in `Description`` from both datasets.
    # These would mess up our matching later, and add no value.
    jobs_df = jobs_df.dropna(subset=["Description"])
    courses_df = courses_df.dropna(subset=["Description"])

    # Some courses have very brief `Descriptions``, which only mention prerequisites - useless for matching.
    # These tend to be brief, so to avoid matching jobs with courses that are not relevant, we'll
    # filter out any descriptions that have less than `min_description_size` characters.
    jobs_df = jobs_df[jobs_df["Description"].str.len() >= min_description_size]
    courses_df = courses_df[courses_df["Description"].str.len() >= min_description_size]

    # Tokenize and lemmatize the job descriptions.
    job_tokens = jobs_df["Description"].apply(tokenize_lemmatize_text)
    course_tokens = courses_df["Description"].apply(tokenize_lemmatize_text)

    # Get the TF-IDF vectors. Here, we vectorize jobs first - as they have MUCH larger descriptions and vocabs,
    # and we can reuse the vocabulary for the course descriptions. This ensures they match for the similarity
    # matrix computation.
    job_vectors, vocab = tf_idf_vectorize(job_tokens)
    course_vectors, _ = tf_idf_vectorize(course_tokens, vocabulary=vocab)

    # Get the cosine similarity between the job and course vectors.
    similarity_matrix = cosine_similarity(job_vectors, course_vectors)

    matching_courses = list()

    # For each job, get at most the top N courses that match which are above the threshold.
    for i, job_id in enumerate(jobs_df["JobId"]):
        # Argsort the sim. matrix, get last N (higher sim.), and reverse to get descending order.
        for j in similarity_matrix[i].argsort()[::-1]:
            # Only add course if similarity is above threshold.
            if similarity_matrix[i][j] > threshold:
                matching_courses.append([
                                    job_id,
                                    courses_df.iloc[j]["CRN"],
                                    similarity_matrix[i][j],
                                ])
                
    matching_courses_df = pd.DataFrame(matching_courses, columns=["JobId", "CRN", "Similarity"])

    if join_all_courses_cols:
        matching_courses_df = matching_courses_df.join(
            courses_df.set_index("CRN"), on="CRN"
        )

        if merge_sections:
            # Merge all sections of the same course.
            matching_courses_df = matching_courses_df.drop_duplicates(
                subset=["Year", "Term", "Subject", "Number"]
            )

    return matching_courses_df.head(N)

