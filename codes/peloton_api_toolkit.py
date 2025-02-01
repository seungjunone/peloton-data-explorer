def handle_api_error(response, context="Peloton Public API request"):
    """
    Handles API errors and prints informative messages.

    Args:
        response: The requests.Response object.
        context: A string describing the context of the error (e.g., "authentication", "data retrieval").

    Returns:
        None if the error is handled, or raises the exception if it's unrecoverable.
    """

    try:
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    except requests.exceptions.HTTPError as e:
        print(f"Error during {context}: {e}")
        try: # Attempt to parse JSON error response for more details.
            error_data = response.json()
            if isinstance(error_data, dict): # Check if it's a dictionary
                error_message = error_data.get("message") or error_data.get("error") or "No detailed error message provided."
                print(f"API Error Details: {error_message}")
            else:
                print(f"Response Content: {response.text}") # Print the raw response if not json
        except json.JSONDecodeError:
            print(f"Response Content: {response.text}")  # Print the raw response if JSON parsing fails
        return None

    except requests.exceptions.RequestException as e: # Catch other request exceptions
        print(f"Error during {context}: {e}")
        return None

    except Exception as e:  # Catch any other unexpected exceptions
        print(f"An unexpected error occurred during {context}: {e}")
        return None

    return None # If no error, return None



def get_user_id(s,
                api_base_url="https://api.onepeloton.com",
                path_auth="/auth/login",
                peloton_username=None,  # Initialize to None
                peloton_password=None
               ):
    """
    Retrieves the Peloton user ID.

    Args:
        s: A requests session object.
        api_base_url: The base URL for the Peloton API. Defaults to "https://api.onepeloton.com".
        path_auth: The API path for authentication. Defaults to "/auth/login".
        peloton_username: The Peloton username. If None, tries to get it from environment variables.
        peloton_password: The Peloton password. If None, tries to get it from environment variables.

    Returns:
        The Peloton user ID, or None if an error occurs.
    """

    if peloton_username is None:
        peloton_username = os.environ.get('peloton_user_name')
    if peloton_password is None:
        peloton_password = os.environ.get('peloton_password')

    if not peloton_username or not peloton_password:
        print("Error: Peloton username and password must be provided (either as arguments or environment variables).")
        return None

    params_auth_query = {'username_or_email': peloton_username, 'password': peloton_password}
     
    try:
        response = s.post(api_base_url + path_auth, json = params_auth_query)
        if handle_api_error(response, context="userID retrieval"): 
            return None

        userID = json.loads(response.text)['user_id'] 
        return userID

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None



def extract_user_overview(s,
                          userID,
                          api_base_url="https://api.onepeloton.com"
                          ):
    
    """Retrieves the user overview data from the Peloton API.

    Args:
        s: A requests.Session object, likely already authenticated.
        userID: The ID of the user whose overview to retrieve.
        api_base_url: The base URL for the Peloton API. Defaults to the public API URL.

    Returns:
        A dictionary containing the user overview data (parsed JSON).

    Raises:
        ValueError: If the Peloton API returns an error (non-200 status code) 
                    or returns a non-JSON response.  The ValueError message 
                    will contain details about the API error.
        Other Exceptions: Any other exceptions raised during the API call
                         (e.g., connection errors) will be re-raised.
    """
    
    path_user_overview = f'/api/user/{userID}/overview'
    headers = {
        'Peloton-Platform': 'web'
    }
    
    try:
        response = s.get(api_base_url + path_user_overview, headers = headers)
        if handle_api_error(response, context="user overview retrieval"): 
            return None

        response_json = json.loads(response.text)
        return(response_json)

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None