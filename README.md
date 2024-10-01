# Yandex TTS Web Application

## Overview

This repository contains a web-based application built using Python and Yandex's Text-to-Speech (TTS) API. It allows users to input text and convert it into speech dynamically. The app is designed for ease of use, providing an interface to quickly generate and download audio files in various formats.

## Features

- **Yandex TTS Integration**: Uses Yandex's TTS API to convert user input text into high-quality speech.
- **Multi-Language Support**: The app supports multiple languages and accents available through Yandex TTS.
- **Real-Time Conversion**: Instantly converts text into speech and provides the audio file for download.
- **Audio Format**: Outputs the speech in `.ogg` format, which is highly compressed and suitable for web use.
- **User-Friendly Interface**: A simple and clean web interface for easy interaction.
  
## Technologies Used

- **Python**: The primary programming language used to handle the TTS requests and process the API data.
- **Yandex TTS API**: Core of the application, responsible for converting the text to speech.
- **Flask**: A lightweight Python web framework used to build the web interface.
- **HTML/CSS/JavaScript**: For designing the front-end interface.
- **Poetry**: Python dependency management.

## Installation

### Prerequisites

- Python 3.8 or higher
- [Yandex API Key](https://cloud.yandex.com/services/speechkit) (for using the Yandex TTS service)
- Poetry for dependency management

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/e-Nicko/yandex-tts-codesandbox-web-app.git
   ```
2. Navigate to the project directory:
   ```bash
   cd yandex-tts-codesandbox-web-app
   ```
3. Install the required dependencies:
   ```bash
   poetry install
   ```

4. Set your Yandex API key as an environment variable:
   ```bash
   export YANDEX_API_KEY="your_api_key_here"
   ```

5. Run the web application:
   ```bash
   python main.py
   ```

6. Open your browser and navigate to:
   ```
   http://localhost:8000/ui
   ```

## Usage

1. Enter the text you wish to convert into speech in the input box.
2. Select the desired language and accent (if applicable).
3. Click on the "Convert" button.
4. After processing, the application will generate an audio file, which can be played directly in the browser or downloaded for offline use.

## Project Structure

```plaintext
yandex-tts-codesandbox-web-app/
│
├── static/                   # Static files (CSS, JS)
├── templates/                # HTML templates for the web app
├── main.py                   # Main entry point for running the application
├── utils.py                  # Helper functions for interacting with Yandex TTS API
├── requirements.txt          # Python dependencies
├── poetry.lock               # Lock file for dependency versions
└── pyproject.toml            # Configuration for Poetry
```

## API Key Setup

This app requires a Yandex API key to function properly. You can generate your own key by following these steps:

1. Sign up for Yandex Cloud [here](https://cloud.yandex.com/).
2. Navigate to the [SpeechKit service](https://cloud.yandex.com/services/speechkit) and generate an API key.
3. Set the key as an environment variable:
   ```bash
   export YANDEX_API_KEY="your_api_key_here"
   ```

## Contributing

Contributions are welcome! To get started:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
