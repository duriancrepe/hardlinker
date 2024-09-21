import os
import json
import urllib.parse
import urllib.request
import configparser
import re

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Extract OMDb and TMDb settings from the configuration file
OMDB_API_KEY = config.get('OMDb', 'omdb_api_key')
OMDB_API_URL = config.get('OMDb', 'omdb_api_url')
TMDB_API_KEY = config.get('TMDb', 'tmdb_api_key')
SOURCE_MAP_FILE = config.get('OMDb', 'source_map_file', fallback='hardlink_mappings.txt')
DESTINATION_MAP_FILE = config.get('OMDb', 'destination_map_file', fallback='hardlink_mappings_omdb.txt')
FAILED_QUERIES_LOG_FILE = config.get('Settings', 'failed_queries_log_file', fallback='failed_queries.log')

def remove_invalid_characters(name):
    """Remove invalid filesystem characters from the name."""
    return re.sub(r'[\/:*?"<>|]', '', name)

def clean_query(query):
    """Clean the query string by replacing underscores with spaces, removing non-alphanumeric characters, and normalizing spaces."""
    query = query.replace('_', ' ').strip()
    query = re.sub(r'\s+', ' ', query)  # Replace multiple spaces with a single space
    return re.sub(r'[^a-zA-Z0-9\s]', '', query)

def attempt_query(url, failed_queries, clean_title):
    """Attempt to query a URL and log any errors."""
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            return json.loads(data)
    except Exception as e:
        failed_queries.append(f"Error querying API for '{clean_title}': {e}. URL: {url}\n")
        return None

def query_api(title, failed_queries, api_type):
    """Query the appropriate API and return the title and year."""
    clean_title = clean_query(title)
    query = urllib.parse.quote(clean_title)

    if api_type == "tmdb_tv":
        url = f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_API_KEY}&query={query}"
    elif api_type == "tmdb_movie":
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    else:  # OMDb
        url = f"{OMDB_API_URL}?t={query}&apikey={OMDB_API_KEY}"

    result = attempt_query(url, failed_queries, clean_title)

    if result and result.get("results"):
        if api_type == "tmdb_tv":
            title = result['results'][0]['name']
            year = result['results'][0]['first_air_date'][:4] if 'first_air_date' in result['results'][0] else 'Unknown'
        elif api_type == "tmdb_movie":
            title = result['results'][0]['title']
            year = result['results'][0]['release_date'][:4] if 'release_date' in result['results'][0] else 'Unknown'
        else:  # OMDb
            print(f"Successful OMDb query for: {result.get('Title')} ({result.get('Year')})")
            return result.get("Title"), result.get("Year").rstrip('–')  # Trim trailing dash

        print(f"Successful {api_type} query for: {title} ({year})")
        return title, year

    # Try shorter query (first 3 tokens)
    tokens = clean_title.split()
    if len(tokens) >= 3:
        three_token_query = ' '.join(tokens[:3])
        if three_token_query != clean_title:
            return query_api(three_token_query, failed_queries, api_type)

    # Try shorter query (first 2 tokens)
    if len(tokens) >= 2:
        two_token_query = ' '.join(tokens[:2])
        if two_token_query != clean_title:
            return query_api(two_token_query, failed_queries, api_type)

    return None, None  # Return None if no valid query can be formed

def main():
    """Create a new mappings file using the OMDb and TMDb APIs."""
    new_map_file = DESTINATION_MAP_FILE
    failed_queries = []

    # Load existing mappings to skip them
    existing_mappings = set()
    if os.path.exists(new_map_file):
        with open(new_map_file, 'r') as f:
            for line in f:
                original_name, _ = line.strip().split(':')
                existing_mappings.add(original_name)

    with open(SOURCE_MAP_FILE, 'r') as f:
        mappings = []
        for line in f:
            original_name, cleaned_name = line.strip().split(':')
            if original_name in existing_mappings:
                continue  # Skip already processed items
            
            # First try TMDb TV shows
            title, year = query_api(cleaned_name, failed_queries, "tmdb_tv")

            # If not found, try TMDb movies
            if not title or not year:
                title, year = query_api(cleaned_name, failed_queries, "tmdb_movie")

            # If still not found, try OMDb
            if not title or not year:
                title, year = query_api(cleaned_name, failed_queries, "omdb")

            if title and year:
                title = remove_invalid_characters(title)  # Remove invalid characters
                mappings.append(f"{original_name}:{title} ({year})\n")

    # Write the new mappings to the destination file
    with open(new_map_file, 'w') as new_f:
        new_f.writelines(mappings)

    # Write the failed queries to the log file
    if failed_queries:
        with open(FAILED_QUERIES_LOG_FILE, 'w') as failed_f:
            failed_f.writelines(failed_queries)

    print(f"New mappings file created: {new_map_file}")
    if failed_queries:
        print(f"Failed queries logged in: {FAILED_QUERIES_LOG_FILE}")

if __name__ == "__main__":
    main()
