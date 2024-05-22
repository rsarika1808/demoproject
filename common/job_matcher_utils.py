# job_matcher_utils.py

def calculate_similarity(job_description, candidate_profile):
    """
    Calculate the similarity between a job description and a candidate profile.
    This function can be customized based on specific requirements.
    """
    # Example implementation: Count the number of matching words
    job_words = set(job_description.lower().split())
    candidate_words = set(candidate_profile.lower().split())
    common_words = job_words.intersection(candidate_words)
    similarity_score = len(common_words) / len(job_words)
    return similarity_score

def find_best_match(job_descriptions, candidate_profiles):
    """
    Find the best match between job descriptions and candidate profiles.
    """
    best_match = None
    best_similarity = 0

    for job_desc in job_descriptions:
        for candidate_profile in candidate_profiles:
            similarity = calculate_similarity(job_desc, candidate_profile)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = (job_desc, candidate_profile)

    return best_match


if __name__ =="__main__":
    # Additional utility functions can be added here as needed
    # from job_matcher_utils import calculate_similarity, find_best_match

    # Example usage:
    job_descriptions = ["Software Engineer", "Data Analyst", "Project Manager"]
    candidate_profiles = ["Experienced in Python and Java", "Skilled in data analysis techniques", "Certified project management professional"]

    best_match = find_best_match(job_descriptions, candidate_profiles)
    print("Best match:", best_match)