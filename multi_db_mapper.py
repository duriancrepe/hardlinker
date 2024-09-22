
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
    """
    Clean the query string by replacing underscores with spaces,
    removing symbolic characters, and normalizing spaces.
    Preserves alphanumeric characters, Asian characters, and spaces.
    """
    # Replace underscores with spaces
    query = query.replace('_', ' ').strip()
    
    # Remove symbolic characters, but keep alphanumeric, Asian characters, and spaces
    query = re.sub(r'[^\w\s\u3000-\u9FFF\uFF00-\uFFEF]', '', query, flags=re.UNICODE)
    
    # Normalize spaces (replace multiple spaces with a single space)
    query = re.sub(r'\s+', ' ', query)
    
    return query

def attempt_query(url, failed_queries, clean_title):
    """Attempt to query a URL and log any errors or failed queries."""
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
            result = json.loads(data)
            if not result or (isinstance(result, dict) and result.get('Response') == 'False'):
                failed_queries.append(f"No valid result for '{clean_title}'. URL: {url}\n")
                return None
            return result
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

    if result:
        if api_type == "tmdb_tv":
            if result.get("results") and len(result["results"]) > 0:
                title = result['results'][0]['name']
                year = result['results'][0]['first_air_date'][:4] if 'first_air_date' in result['results'][0] else 'Unknown'
            else:
                failed_queries.append(f"No results found for TMDb TV query: '{clean_title}'. URL: {url}\n")
                return None, None
        elif api_type == "tmdb_movie":
            if result.get("results") and len(result["results"]) > 0:
                title = result['results'][0]['title']
                year = result['results'][0]['release_date'][:4] if 'release_date' in result['results'][0] else 'Unknown'
            else:
                failed_queries.append(f"No results found for TMDb Movie query: '{clean_title}'. URL: {url}\n")
                return None, None
        else:  # OMDb
            if result.get('Response') == 'True':
                title = result.get('Title')
                year = result.get('Year', 'Unknown').rstrip('–')  # Trim trailing dash
            else:
                failed_queries.append(f"No results found for OMDb query: '{clean_title}'. URL: {url}\n")
                return None, None

        print(f"Successful {api_type} query for: {title} ({year})")
        return title, year

    # If we reach here, it means the query failed
    failed_queries.append(f"Failed {api_type} query for: '{clean_title}'. URL: {url}\n")

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
    processed_items = []

    # Load existing mappings to skip them
    existing_mappings = set()
    if os.path.exists(new_map_file):
        with open(new_map_file, 'r') as f:
            for line in f:
                original_name, _ = line.strip().split(':', 1)
                existing_mappings.add(original_name)

    with open(SOURCE_MAP_FILE, 'r') as f, open(new_map_file, 'a') as new_f:
        for line_number, line in enumerate(f, 1):
            try:
                original_name, cleaned_name = line.strip().split(':', 1)
            except ValueError:
                failed_queries.append(f"Line {line_number}: Invalid format - {line.strip()}\n")
                print(f"Line {line_number}: Invalid format - {line.strip()}")
                continue

            if original_name in existing_mappings:
                processed_items.append(f"Line {line_number}: Skipped (already processed) - {original_name}\n")
                print(f"Line {line_number}: Skipped (already processed) - {original_name}")
                continue  # Skip already processed items
            
            processed_items.append(f"Line {line_number}: Processing - {original_name}\n")
            print(f"Line {line_number}: Processing - {original_name}")
            
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
                new_mapping = f"{original_name}:{title} ({year})"
                new_f.write(f"{new_mapping}\n")
                processed_items.append(f"Line {line_number}: Mapped - {new_mapping}\n")
                print(f"Line {line_number}: Mapped - {new_mapping}")
            else:
                # Write the original name and cleaned name without year when all APIs fail
                new_mapping = f"{original_name}:{cleaned_name}"
                new_f.write(f"{new_mapping}\n")
                failed_queries.append(f"Line {line_number}: No valid result found for: '{cleaned_name}' after trying all APIs. Using cleaned name.\n")
                processed_items.append(f"Line {line_number}: Failed - {new_mapping}\n")
                print(f"Line {line_number}: Failed - {new_mapping}")

    # Write the failed queries to the log file
    with open(FAILED_QUERIES_LOG_FILE, 'w') as failed_f:
        failed_f.writelines(failed_queries)

    # Write processed items to a new log file
    processed_items_log_file = 'processed_items.log'
    with open(processed_items_log_file, 'w') as processed_f:
        processed_f.writelines(processed_items)

    print(f"\nMappings file updated: {new_map_file}")
    print(f"Failed queries logged in: {FAILED_QUERIES_LOG_FILE}")
    print(f"Processed items logged in: {processed_items_log_file}")

if __name__ == "__main__":
    main()
