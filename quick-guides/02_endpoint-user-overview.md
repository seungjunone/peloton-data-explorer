```python
import requests
import json
import pandas as pd
import os
from pprint import pprint
```

We've successfully accessed the Peloton API and retrieved valuable data. But as we explore more endpoints, we'll likely encounter similar patterns in our code. Repeating the same code blocks for different API calls can quickly become tedious and inefficient.

Let's transform some of our existing code into reusable functions, making our Peloton data exploration more efficient and enjoyable.

## Authenticate and Retrive userID

From our previous exercise, we can construct the following function to:

* Get user credentials from environment variables.
* Post an API request given the username/email and password.
* Retrieve the userID (access token) from the response.

```
def get_user_id(s, api_base_url, path_auth):
    
    peloton_username = os.environ.get('peloton_user_name') 
    peloton_password = os.environ.get('peloton_password') 
    params_auth_query = {'username_or_email': peloton_username, 'password': peloton_password}
    
    response = s.post(api_base_url + path_auth, json = params_auth_query)
    userID = json.loads(response.text)['user_id']
    
    return(userID)
```

This function, however, doesn't handle API errors gracefully. For instance, if the credentials are incorrect, it will return an ambiguous `KeyError`.

```
Cell In[28], line 8, in get_user_id(s, api_base_url, path_auth)
      5 params_auth_query = {'username_or_email': peloton_username, 'password': peloton_password}
      7 response = s.post(api_base_url + path_auth, json = params_auth_query)
----> 8 userID = json.loads(response.text)['user_id']
     10 return(userID)

KeyError: 'user_id'
```

Let's create a `handle_api_error` function to provide more informative error messages upon failure.

## Implementing handle_api_error

A robust error handler should check the HTTP status code and the JSON response for specific error messages from the Peloton API.  Let's reate a function that provides more informative error messages, making it easier to debug issues with the Peloton API. More specificially, it will handle following checks:

* Status Code Check: Checks if the HTTP status code is 200. Any other code indicates an error.
* Clear Error Messages: Raises a ValueError with a descriptive message, including the status code and the raw response text (for debugging).
* Error Handling in get_user_id: The get_user_id function now calls handle_api_error after making the API request. This centralizes the error handling logic.


```python
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
```

This function will also handles the possibility of unexpected responses from the API, making the code more robust. 

* JSON Error Parsing: Attempts to parse the JSON response. Peloton's API should return error details in JSON format. This allows us to extract and display a more specific error message. Includes a check for the 'detail' key as well as 'message', as the API may return errors with different structures.
* Handles Invalid JSON: Includes a try...except block to catch json.JSONDecodeError in case the API returns a non-JSON error response. This prevents cryptic errors if the API behaves unexpectedly.

## (Refactor) Authenticate and Retrive userID

Let's enhance the `get_user_id` function to leverage the `handle_api_erro`r function for robust error management.  We'll also incorporate default values for the api_base_url and path_auth parameters to simplify usage.  Finally, we'll make the user credentials optional, allowing for more flexible authentication methods.


```python
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
```

Let's see how it handles authentification error.


```python
session = requests.Session()
userID = get_user_id(session, peloton_username = 'auth_error_test@email.com')
```

    Error during userID retrieval: 401 Client Error: Unauthorized for url: https://api.onepeloton.com/auth/login
    API Error Details: Login failed
    An unexpected error occurred: 'user_id'


As shown above, now when `get_user_id` fails, it returns a clear error message that shows login failed with credential error.

Let's do the same for the data extraction!

## Extract and Clean User Overview Output

In this section, we'll develop a suite of functions to process the raw user overview data retrieved from the Peloton API.  These functions will handle the extraction, transformation, and cleaning of the data, ultimately converting it into a structured, tabular format suitable for analysis.  Specifically, we will define:

* `extract_user_overview`: This function will use the userID obtained from get_user_id to query the Peloton API's user overview endpoint. It will then parse the JSON response and return the data in a usable format.
* `coerce_columns`: This utility function will address data type inconsistencies and format issues within the raw data. It will handle conversions such as Unix timestamps to datetime objects to ensure data readability and consistency.
* `clean_user_overview`: This core function will take the processed JSON output from `extract_user_overview` and, with the help of `coerce_columns`, transform it into several pandas DataFrames. This tabular structure will facilitate quick review and downstream data analysis.

Let's start with `extract_user_overview`.



```python
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
```


```python
session = requests.Session()
userID = get_user_id(session)
response_json = extract_user_overview(session, userID)
```

As shown below, the response_json now contains the user overivew data - namely, achievement coutns, personal records, streaks, and workout counts.


```python
# remove id from displaying, as it is a sensitive record.
def remove_key_comprehension(data, key_to_remove):
  if isinstance(data, dict):
    return {k: v for k, v in data.items() if k != key_to_remove}
  return data # if not dict

new_data = remove_key_comprehension(response_json, "id")
pprint(new_data, depth = 2)
```

    {'achievement_counts': {'achievements': [...], 'total_count': 1650},
     'personal_records': [{...}],
     'streaks': {'best_weekly': 111,
                 'current_daily': 0,
                 'current_weekly': 114,
                 'start_date_of_current_daily': None,
                 'start_date_of_current_weekly': 1669792908},
     'workout_counts': {'total_workouts': 1765, 'workouts': [...]}}


Let's now write functions to show each entries in dataframe with correct datatype.


```python
def coerce_columns(df, type_dict, date_format=None, date_unit=None):
  """
  Coerces columns in a DataFrame to specified types, including date conversion.

  Args:
    df: The pandas DataFrame.
    type_dict: A dictionary mapping column names to data types.
    date_format: (Optional) A string specifying the date format 
                 if any columns need to be converted to datetime.

  Returns:
    The DataFrame with coerced columns.
  """
  for col, col_type in type_dict.items():
    try:
      if col_type == 'datetime' and date_format:
        df[col] = pd.to_datetime(df[col], format=date_format)
      elif col_type == 'datetime' and date_unit:
        df[col] = pd.to_datetime(df[col], unit=date_unit)
      else:
        df[col] = df[col].astype(col_type)
    except ValueError as e:
      print(f"Error converting column {col} to {col_type}: {e}")
  return (df)
```


```python
def clean_user_overview(response_json):
    """Cleans and structures the user overview data from the Peloton API.

    Args:
        response_json: A dictionary containing the JSON response from the 
                       Peloton user overview API endpoint.

    Returns:
        A tuple containing four pandas DataFrames:
            - df_personal_records: Personal records data.
            - df_streaks: Streaks data.
            - df_achievements: Achievements data.
            - df_workout_counts: Workout counts data.

        Returns empty DataFrame for any missing keys.
    """ 
    
    try:
        # personal_records
        df_personal_records = pd.DataFrame(response_json['personal_records'][0]['records'])
        col_type_personal_records = {
            'slug':'int',
            'value':'int',
            'raw_value':'float',
            'workout_date': 'datetime'
        }
        df_personal_records = coerce_columns(df_personal_records, col_type_personal_records, date_format = 'mixed')
        df_personal_records = df_personal_records.sort_values('slug')

        # streaks
        df_streaks = pd.DataFrame([response_json['streaks']])
        col_type_streaks = {
            'start_date_of_current_weekly':'datetime',
            'start_date_of_current_daily':'datetime'
        }    
        df_streaks = coerce_columns(df_streaks, col_type_streaks, date_unit = 's')   

        # dachievements
        df_achievements =  pd.DataFrame(response_json['achievement_counts']['achievements'])
        achievement_template_norm = pd.json_normalize(df_achievements['template'])
        df_achievements = pd.concat([df_achievements.drop(columns=['template']), achievement_template_norm], axis=1)

        # workout counts
        df_workout_counts = pd.DataFrame(response_json['workout_counts']['workouts'])

        return(df_personal_records, df_streaks, df_achievements, df_workout_counts)

    except (KeyError, TypeError) as e:
        print(f"Error processing user overview data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame() 
```


```python
session = requests.Session()
userID = get_user_id(session)

response_json = extract_user_overview(session, userID)
df_personal_records, df_streaks, df_achievements, df_workout_counts = clean_user_overview(response_json)
```

Hmmm, the personal records shows that I should retake 75 min class - as its output is far below shorter length classes.


```python
df_personal_records.head(10)[['name', 'value', 'unit']]
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
      <th>value</th>
      <th>unit</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>4</th>
      <td>5 min</td>
      <td>71</td>
      <td>kj</td>
    </tr>
    <tr>
      <th>5</th>
      <td>10 min</td>
      <td>148</td>
      <td>kj</td>
    </tr>
    <tr>
      <th>6</th>
      <td>15 min</td>
      <td>173</td>
      <td>kj</td>
    </tr>
    <tr>
      <th>7</th>
      <td>20 min</td>
      <td>460</td>
      <td>kj</td>
    </tr>
    <tr>
      <th>8</th>
      <td>30 min</td>
      <td>572</td>
      <td>kj</td>
    </tr>
    <tr>
      <th>0</th>
      <td>45 min</td>
      <td>883</td>
      <td>kj</td>
    </tr>
    <tr>
      <th>1</th>
      <td>60 min</td>
      <td>1056</td>
      <td>kj</td>
    </tr>
    <tr>
      <th>2</th>
      <td>75 min</td>
      <td>587</td>
      <td>kj</td>
    </tr>
    <tr>
      <th>3</th>
      <td>90 min</td>
      <td>1554</td>
      <td>kj</td>
    </tr>
  </tbody>
</table>
</div>



I forgot to do my Peloton workout yesterday, which unfortunately reset my daily streak. Time for a fresh start!


```python
df_streaks.T
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>0</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>current_weekly</th>
      <td>114</td>
    </tr>
    <tr>
      <th>best_weekly</th>
      <td>111</td>
    </tr>
    <tr>
      <th>start_date_of_current_weekly</th>
      <td>2022-11-30 07:21:48</td>
    </tr>
    <tr>
      <th>current_daily</th>
      <td>0</td>
    </tr>
    <tr>
      <th>start_date_of_current_daily</th>
      <td>NaT</td>
    </tr>
  </tbody>
</table>
</div>



In fact, I'll be aiming for another `60-Day Streak` this year!


```python
df_achievements[df_achievements['name'].str.contains('Day Streak')]
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>count</th>
      <th>id</th>
      <th>name</th>
      <th>slug</th>
      <th>image_url</th>
      <th>description</th>
      <th>animated_image_url</th>
      <th>kinetic_token_background</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>98</th>
      <td>64</td>
      <td>5298b832e2274ad59cf8857240440fb2</td>
      <td>3-Day Streak</td>
      <td>3_day_streak</td>
      <td>https://s3.amazonaws.com/peloton-achievement-i...</td>
      <td>Awarded for working out 3 days in a row.</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>99</th>
      <td>26</td>
      <td>013f0b69303d414ca2d73d1aacc04a0e</td>
      <td>5-Day Streak</td>
      <td>5_day_streak</td>
      <td>https://s3.amazonaws.com/peloton-achievement-i...</td>
      <td>Awarded for working out 5 days in a row.</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>100</th>
      <td>19</td>
      <td>ca11fdd59d6342809084532531f18ed9</td>
      <td>7-Day Streak</td>
      <td>7_day_streak</td>
      <td>https://s3.amazonaws.com/peloton-achievement-i...</td>
      <td>Awarded for working out 7 days in a row.</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>101</th>
      <td>10</td>
      <td>4dafabb0092b4870bff8ef393dc1acbe</td>
      <td>10-Day Streak</td>
      <td>10_day_streak</td>
      <td>https://s3.amazonaws.com/peloton-achievement-i...</td>
      <td>Awarded for working out 10 days in a row.</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>102</th>
      <td>4</td>
      <td>bca3ee6e99f24848aa8457eb6115c671</td>
      <td>20-Day Streak</td>
      <td>20_day_streak</td>
      <td>https://s3.amazonaws.com/peloton-achievement-i...</td>
      <td>Awarded for working out 20 days in a row.</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>103</th>
      <td>3</td>
      <td>dc9b61069ca04dbeaba9555199bc5cc6</td>
      <td>30-Day Streak</td>
      <td>30_day_streak</td>
      <td>https://s3.amazonaws.com/peloton-achievement-i...</td>
      <td>Awarded for working out 30 days in a row.</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>104</th>
      <td>2</td>
      <td>49cf39dbb14c41c5a2f6bf0f15046b7d</td>
      <td>45-Day Streak</td>
      <td>45_day_streak</td>
      <td>https://s3.amazonaws.com/peloton-achievement-i...</td>
      <td>Awarded for working out 45 days in a row.</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>105</th>
      <td>1</td>
      <td>529f22af30ba45a0a501b8542ad3b99c</td>
      <td>60-Day Streak</td>
      <td>60_day_streak</td>
      <td>https://s3.amazonaws.com/peloton-achievement-i...</td>
      <td>Awarded for working out 60 days in a row.</td>
      <td>None</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>



Lastly my workout count indicates a good balance of cycling, stretching, and strength workouts. However, there's room for improvement, for example, by incorporating more yoga classes.


```python
df_workout_counts
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
      <th>slug</th>
      <th>count</th>
      <th>icon_url</th>
      <th>workout_name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Cycling</td>
      <td>cycling</td>
      <td>749</td>
      <td>https://s3.amazonaws.com/static-cdn.pelotoncyc...</td>
      <td>Cycling</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Stretching</td>
      <td>stretching</td>
      <td>473</td>
      <td>https://s3.amazonaws.com/static-cdn.pelotoncyc...</td>
      <td>Stretching</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Strength</td>
      <td>strength</td>
      <td>394</td>
      <td>https://s3.amazonaws.com/static-cdn.pelotoncyc...</td>
      <td>Strength</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Walking</td>
      <td>walking</td>
      <td>66</td>
      <td>https://s3.amazonaws.com/static-cdn.pelotoncyc...</td>
      <td>Walking</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Rowing</td>
      <td>caesar</td>
      <td>31</td>
      <td>https://s3.amazonaws.com/static-cdn.pelotoncyc...</td>
      <td>Rowing</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Meditation</td>
      <td>meditation</td>
      <td>23</td>
      <td>https://s3.amazonaws.com/static-cdn.pelotoncyc...</td>
      <td>Meditation</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Cardio</td>
      <td>cardio</td>
      <td>17</td>
      <td>https://s3.amazonaws.com/static-cdn.pelotoncyc...</td>
      <td>Cardio</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Running</td>
      <td>running</td>
      <td>10</td>
      <td>https://s3.amazonaws.com/static-cdn.pelotoncyc...</td>
      <td>Running</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Bike Bootcamp</td>
      <td>bike_bootcamp</td>
      <td>1</td>
      <td>https://s3.amazonaws.com/static-cdn.pelotoncyc...</td>
      <td>Bike Bootcamp</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Yoga</td>
      <td>yoga</td>
      <td>1</td>
      <td>https://s3.amazonaws.com/static-cdn.pelotoncyc...</td>
      <td>Yoga</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Row Bootcamp</td>
      <td>caesar_bootcamp</td>
      <td>0</td>
      <td>https://s3.amazonaws.com/static-cdn.pelotoncyc...</td>
      <td>Row Bootcamp</td>
    </tr>
    <tr>
      <th>11</th>
      <td>Tread Bootcamp</td>
      <td>circuit</td>
      <td>0</td>
      <td>https://s3.amazonaws.com/static-cdn.pelotoncyc...</td>
      <td>Tread Bootcamp</td>
    </tr>
  </tbody>
</table>
</div>


