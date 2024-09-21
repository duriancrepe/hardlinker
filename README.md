
# Hardlink Creator

This project provides a tool for creating hardlinks between a source directory and a destination directory. It includes both a main implementation and a raw implementation, along with additional utilities for mapping and handling movie metadata.

## Table of Contents

1. [Overview](#overview)
2. [Files](#files)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [Components](#components)

## Overview

The Hardlink Creator is designed to create hardlinks from files in a source directory to a destination directory. This can be useful for managing large file collections, especially media files like movies, without duplicating the actual data on disk.

## Files

- `main.py`: The main entry point of the application.
- `hardlinker.py`: Contains the core hardlinking functionality.
- `mapper.py`: Provides mapping utilities for file organization.
- `omdb_mapper.py`: Handles mapping of movie metadata using the OMDB API.
- `raw_hardlinker.py`: A more basic implementation of the hardlinking process.
- `config.ini`: Configuration file containing settings for the application.

## Configuration

The application uses a `config.ini` file for its settings. This file includes:

- API keys for OMDb and TMDb
- Source and destination folder paths
- File paths for various mappings and logs
- Keywords for file processing

Make sure to update the `config.ini` file with your specific settings before running the application.

## Usage

To use the main implementation:

```
python main.py
```

For the raw implementation:

```
python raw_hardlinker.py
```

Both scripts will use the settings specified in the `config.ini` file by default. There's no need to provide command-line arguments unless you want to override specific settings.

## Components

### main.py

This is the main entry point of the application. It orchestrates the hardlinking process using the other modules and the settings from `config.ini`.

### hardlinker.py

Contains the core functionality for creating hardlinks between the source and destination directories.

### mapper.py

Provides utilities for mapping files, organizing the hardlinked files in the destination directory based on the configuration.

### omdb_mapper.py

Handles the mapping of movie metadata using the OMDB (Open Movie Database) API. This is useful for organizing movie files with additional information.

### raw_hardlinker.py

A more basic implementation of the hardlinking process, possibly without some of the additional features or optimizations found in the main implementation.

### config.ini

Configuration file that contains all the necessary settings for the application, including:
- OMDb and TMDb API keys and URLs
- Source and destination folder paths
- Mapping file paths
- Keywords for file processing
- Log file paths

---

For more detailed information about each component and configuration options, please refer to the individual Python files, their docstrings, and the `config.ini` file.
