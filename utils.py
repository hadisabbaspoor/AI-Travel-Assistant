from pypdf import PdfReader
import pandas as pd
import numpy as np
import json
import re
from langchain.prompts import PromptTemplate
from langchain_openai.llms import OpenAI
from langchain.chains import LLMChain
from langchain.chains import LLMRequestsChain, LLMChain
from datetime import datetime, timedelta
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings

def get_pdf_text(pdf_doc):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_doc (str): Path to the PDF file.
        
    Returns:
        str: Extracted text from the PDF.
    """
    text = ""
    pdf_reader = PdfReader(pdf_doc)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def get_llm_chain_gpt():
    """
    Create a LLM chain for the OpenAI GPT model.
    
    Returns:
        LLMChain: The LLMChain object configured with the prompt template.
    """
    llm = OpenAI(temperature=.7)
    template = """Extract all of the following values: Full Name, Depart, Date of Depart, Arrive, Date of Arrive(just dd.mm.yyyy) from the following data:
        Format the output in JSON and leave missing data blank.
        
        Example 1:
        {{
            "Full Name": "Amir Santoshi",
            "Depart": "London Airport",
            "Date of Depart": "10 April 2020",
            "Arrive": "Berlin Airport",
            "Date of Arrive": "11 April 2020"
        }}

        Example 2:
        {{
            "Full Name": "John Doe",
            "Depart": "New York JFK",
            "Date of Depart": "05 March 2021",
            "Arrive": "Los Angeles LAX",
            "Date of Arrive": "05 March 2021"
        }}

        Here comes the data:
        {contents}
        """

    prompt = PromptTemplate(
        input_variables=["contents"], template=template)
    return LLMChain(prompt=prompt, llm=llm)


def create_docs(user_pdf_list, days_value):
    """
    Iterate over files and create a DataFrame.
    
    Args:
        user_pdf_list (list): List of PDF files.
        days_value (int): Number of days.
        
    Returns:
        DataFrame: A DataFrame containing the extracted data.
    """
    llm_chain = get_llm_chain_gpt()
    row_list = []

    for filename in user_pdf_list:
        print(filename.name)
        raw_data = get_pdf_text(filename)
        llm_extracted_data = llm_chain.invoke(raw_data)['text']
        try:
            # Search for text between '{' and '}'
            match = re.search(r'\{([^{}]*)\}', llm_extracted_data)
            if match:
                json_string = '{' + match.group(1) + '}'
                print(json_string)
                data_dict = json.loads(json_string)
                
                data_dict['Days'] = days_value
                row_list.append(data_dict)
            else:
                return print('No JSON found.')
        except:
            print('Error while parsing string.')

    df = pd.DataFrame(row_list)
    df.head()
    
    return df


# def define_city(arrive):
#     #Search city name based on airport name using OpenAI
#     llm = OpenAI()
#     template = """
#     {query}
#     Just say the name of the city without any additional explanation.
#      YOUR RESPONSE:
#     """
#     prompt= PromptTemplate(
#     input_variables=["query"],
#     template=template,
#     )
#     final_prompt = prompt.format(query = f'In which city is {arrive} located?')
#     city = llm.invoke(final_prompt)
#     return city


def define_city(arrive):
    """
    Search for the city name based on the airport name using embeddings.
    
    Args:
        arrive (str): Airport name.
        
    Returns:
        str: City name corresponding to the airport.
    """
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    df = pd.read_csv('airports.csv')
    df['embedding'] = df['Airport Name'].apply(lambda x: embeddings.embed_query(x))
    airport_name_embedding = embeddings.embed_query(arrive)

    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    df["similarity score"] = df['embedding'].apply(lambda x: cosine_similarity(x, airport_name_embedding))
    city_name = df.sort_values("similarity score", ascending=False).iloc[0]["City"]
    return city_name


def planning_days(city, date, days):
    """
    Plan the days with tourist places to visit in a city.
    
    Args:
        city (str): The city name.
        date (str): The starting date in 'dd MMMM yyyy' format.
        days (int): Number of days to plan.
        
    Returns:
        str: A string with the planned schedule.
    """
    # First chain: Get best places to visit in the city
    template_place = """You should suggest all tourist places to visit in {city}.
    YOUR RESPONSE:
    """
    prompt_template_place = PromptTemplate(
        input_variables=["city"],
        template=template_place
    )
    llm_place = OpenAI(max_tokens= 3000)
    place_chain = LLMChain(llm=llm_place, prompt=prompt_template_place)
    places_response = place_chain.invoke(city)    

    response_schemas = [
    ResponseSchema(name="day1",
                    description="date"),
    ResponseSchema(name="- Morning",
                    description="The name of a tourist place"),
    ResponseSchema(name="- Noon",
                    description="The name of a tourist place"),
    ResponseSchema(name="- Night",
                    description="The name of a tourist place"),
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    # Second chain: Schedule visits based on the number of days
    template_schedule = """With this list of places: {places} , please plan visits from {date} only within {days} days.
    \n{format_instructions}
    YOUR RESPONSE:
    """
    prompt_template_schedule = PromptTemplate(
        input_variables=["places", "date", "days"],
        template=template_schedule,
        partial_variables={"format_instructions": format_instructions}
    )
    llm_schedule = OpenAI(max_tokens= 3000)
    schedule_chain = LLMChain(llm=llm_schedule, prompt=prompt_template_schedule)
    schedule_response = schedule_chain.run({
        "places": places_response,
        "date": date,
        "days": days
    })

    # Adding dates to the schedule
    start_date = datetime.strptime(date, "%d %B %Y")
    schedule_lines = schedule_response.split("\n")
    output_lines = []
    current_day = 0

    for line in schedule_lines:
        if line.startswith("Day"):
            current_day += 1
            current_date = start_date + timedelta(days=current_day - 1)
            formatted_date = current_date.strftime("%d %B %Y")
            output_lines.append(f"Day {current_day}: {formatted_date}")
        else:
            output_lines.append(line)

    review_with_dates = "\n".join(output_lines)
    return review_with_dates


def search_hotel(query):
    """
    Search for hotels in a specific city using Google search.
    
    Args:
        query (str): Search query for the hotels.
        
    Returns:
        dict: A dictionary containing hotel names and their websites.
    """
    response_schemas = [
        ResponseSchema(name="Hotel",
                       description="Name the Hotels"),
        ResponseSchema(name="Website",
                       description="Whats the Website of that Hotel")
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()
    template = """
    Just Name 5 of the best hotels along with their website address.\n{format_instructions}\n{query} .
    """
    PROMPT = PromptTemplate(
    input_variables=["query"],
    template=template,
    partial_variables={"format_instructions": format_instructions}
    )
    llm = OpenAI()
    chain = LLMRequestsChain(llm_chain=LLMChain(llm=llm, prompt=PROMPT))

    inputs = {
    "query":query,
    "url": "https://www.google.com/search?q=" + query.replace(" ", "+"),
    }
    result = chain.invoke(inputs)
    return result