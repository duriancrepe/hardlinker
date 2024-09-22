
# Hardlink Creator

This project provides a tool for creating hardlinks between a source directory and a destination directory. It includes both a mapped implementation and a raw implementation, along with additional utilities for mapping and handling movie metadata from multiple online databases.

## Table of Contents

1. [Overview](#overview)
2. [Files](#files)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [Components](#components)

## Overview

The Hardlink Creator is designed to create hardlinks from files in a source directory to a destination directory. This can be useful for managing large file collections, especially media files like movies and TV shows, without duplicating the actual data on disk.

## Files

- `main.py`: The main entry point of the application.
- `map_hardlinker.py`: Contains the core hardlinking functionality with mapping.
- `mapper.py`: Provides mapping utilities for file organization.
- `multi_db_mapper.py`: Handles mapping of movie and TV show metadata using multiple online databases (OMDb, TMDb).
- `raw_hardlinker.py`: A more basic implementation of the hardlinking process without mapping.
- `config.ini`: Configuration file containing settings for the application.

## Configuration

The application uses a `config.ini` file for its settings. This file includes:

- API keys for OMDb and TMDb
- Source and destination folder paths
- File paths for various mappings and logs
- Keywords for file processing
- Option to use raw hardlinker instead of mapped hardlinker
- Option to merge duplicate destination folders

Make sure to update the `config.ini` file with your specific settings before running the application.

## Usage

To run the application:

```
python main.py
```

The script will use the settings specified in the `config.ini` file.

## Components

### main.py

This is the main entry point of the application. It orchestrates the hardlinking process using the other modules and the settings from `config.ini`.

### map_hardlinker.py

Contains the core functionality for creating hardlinks between the source and destination directories, using mapping information.

### mapper.py

Provides utilities for mapping files, organizing the hardlinked files in the destination directory based on the configuration.

### multi_db_mapper.py

Handles the mapping of movie and TV show metadata using multiple online databases (OMDb, TMDb). This is useful for organizing media files with additional information.

### raw_hardlinker.py

A more basic implementation of the hardlinking process without the additional mapping features.

### config.ini

Configuration file that contains all the necessary settings for the application, including API keys, file paths, and processing options.

---

For more detailed information about each component and configuration options, please refer to the individual Python files, their docstrings, and the `config.ini` file.

