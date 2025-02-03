# Travel Guide Assistant

Travel Guide Assistant is a Python-based web application built using Streamlit and OpenAI's GPT models to help users plan their travel. The app extracts data from travel tickets (PDF format) and provides personalized itineraries, hotel recommendations, and other travel-related information.

## Features

- **Ticket Information Extraction**: Upload your travel ticket in PDF format and extract details such as full name, departure/arrival airports, and travel dates.
- **Itinerary Planning**: Based on your destination city and travel duration, the app generates a customized itinerary with suggested tourist places to visit.
- **Hotel Recommendations**: Get hotel suggestions based on the destination city and your stay duration.
- **Streamlit Web Interface**: A user-friendly web interface to interact with the assistant.

## Requirements

Before running this project, you need to install the following dependencies:

- Python 3.x
- Streamlit
- LangChain
- OpenAI
- Pandas
- NumPy
- PyPDF2
- Sentence-Transformer

You can install all dependencies by running:

```bash
pip install -r requirements.txt
```

## Setup and Installation

1. Clone the repository:

```bash
git clone https://github.com/hadisabbaspoor/AI-Travel-Assistant.git
cd AI-Travel-Assistant
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Ensure you have access to an OpenAI API key. If not, you can get one from [OpenAI](https://openai.com).

4. Run the Streamlit app:

```bash
streamlit run app.py
```

The app should open in your default web browser.

## How It Works

1. **Home Page**:
   - The user is prompted to upload a travel ticket in PDF format and specify the number of days for their trip.
   - The assistant extracts travel details from the ticket, such as name, departure, and arrival dates.

2. **Ticket Info Page**:
   - The user uploads their travel ticket (PDF), and the app extracts key details (e.g., name, departure and arrival cities, dates).
   - The assistant uses this information to provide further recommendations and create an itinerary.

3. **Itinerary Page**:
   - Based on the user's arrival city and the number of days, the assistant generates a daily itinerary with tourist attractions to visit.

4. **Hotels Page**:
   - The app provides hotel recommendations based on the destination city and stay duration, along with hotel websites.

## How to Use

1. Open the web app and navigate to the **"Ticket Info"** page.
2. Upload your travel ticket (PDF format).
3. Enter the number of days you will be staying.
4. Click **"Extract Data"** to process the ticket and get your travel details.
5. Navigate to the **"Itinerary"** page to see a suggested travel itinerary.
6. Visit the **"Hotels"** page for hotel recommendations based on your destination.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This project uses [Streamlit](https://streamlit.io/) for building the web interface.
- OpenAI's GPT models were used for extracting data and generating itineraries.
- The [LangChain](https://www.langchain.com/) library was used for integrating language models and structured prompts.

