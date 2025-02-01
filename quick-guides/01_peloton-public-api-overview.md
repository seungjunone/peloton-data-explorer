# Peloton API Walkthrough

While there isn't an official Peloton API documentation, Peloton communities have shared their own pagckages (e.g. peloton-client-library, pelotonR) and documentations (peloton-unofficial-api).

These resources are somewhat dated, so I've opted to dig into raw outputs from API calls using `request` package.


```python
import requests
import json
import pandas as pd
import os
```

## Step 1. Authenticate

To access the Peloton API, you'll need to authenticate using your user ID and password. The endpoint for authentication is https://api.onepeloton.com/auth/login/.

Here's how to authenticate:

* Prepare the request: Create a JSON object with your user ID and password.
* Make the request: Use the requests library to send a POST request to the authentication endpoint with the user credentials.
* Check the response: The response will be a JSON object that contains an user_id (access token) if the authentication was successful. You can use this access token to authorize future requests to the Peloton API.




```python
peloton_username = os.environ.get('peloton_user_name') 
peloton_password = os.environ.get('peloton_password')

api_base_url = 'https://api.onepeloton.com'
path_auth = '/auth/login'

params_auth_query = {'username_or_email': peloton_username, 'password': peloton_password}

s = requests.Session()
response = s.post(api_base_url + path_auth, json = params_auth_query)

userID = json.loads(response.text)['user_id']
```

Your user_name, password, and access token are sensitive information. Do not share them publicly, and always use best practices in storing credentials. I am using environment variable to store and access the credentials.

## Step 2. Data Extraction

Now that you have an access token, let's start exploring the Peloton API. 

A great place to begin is the /api/user/{user_ID}/overview endpoint. This endpoint provides an overview of your workout history, including the total number of workouts by type, earned achievements, and personal records.

Here's how to use the /api/user/{user_ID}/overview endpoint:

* Construct the URL: Replace {user_ID} with your actual Peloton user ID in the URL.
* Make the request: Use the requests library to send a GET request to the endpoint, including the access token in the Authorization header.


```python
path_user_overview = f'/api/user/{userID}/overview'
headers = {
    'Peloton-Platform': 'web'
}

response = s.get(api_base_url + path_user_overview, headers = headers)
```

Explore the response: The API will return a JSON response containing information about your overall workout history.


```python
response_json = json.loads(response.text)
response_json.keys()
```




    dict_keys(['id', 'workout_counts', 'personal_records', 'streaks', 'achievement_counts'])



From top structure, we can see that this includes data like:

* `Total Workout Counts`: A breakdown of the total number of workouts you've completed across different disciplines (e.g., cycling, strength, yoga). See which categories dominate your fitness routine!
* `Personal Records`: This section reveals your personal records (PRs) for each workout type. (Note: PRs are only available if the workout was completed on a Peloton device, so my data focuses solely on cycling.)
* `Streaks`: Discover your dedication! This section highlights your daily and weekly workout streaks, showcasing your commitment to consistent exercise.
* `Achievements`: Ever wonder how many times you've snagged that 7-day streak badge? This section reveals all your hard-earned Peloton achievements, complete with descriptions, image URLs, and the number of times you've unlocked each one.

To make this data easier to analyze, we'll need to transform it into a more structured format. This involves:

* Converting to Tabular Format: We'll convert the JSON response into a tabular format, like a dataframe, which is ideal for analysis and manipulation.
* Data Type Coercion: We'll ensure that data entries are in the correct format. For example, we'll convert string representations of dates and times into datetime objects for easier manipulation and analysis.

For example, to flatten and show achievement info in tabular format, we first convert it to dataframe, and unnest the template entries.




```python
df_workout_counts = pd.DataFrame(response_json['workout_counts']['workouts'])
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




```python
df_personal_records = pd.DataFrame(response_json['personal_records'][0]['records'])

# workoud_id is removed from the view as it is personal info.
columns_to_exclude = ['workout_id']
columns_to_include = [col for col in df_personal_records.columns if col not in columns_to_exclude]

df_personal_records[columns_to_include].head(5)
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
      <th>value</th>
      <th>raw_value</th>
      <th>unit</th>
      <th>unit_slug</th>
      <th>workout_date</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>45 min</td>
      <td>2700</td>
      <td>883</td>
      <td>882694.27</td>
      <td>kj</td>
      <td>kj</td>
      <td>2024-05-06T09:57:46.552438</td>
    </tr>
    <tr>
      <th>1</th>
      <td>60 min</td>
      <td>3600</td>
      <td>1056</td>
      <td>1056107.31</td>
      <td>kj</td>
      <td>kj</td>
      <td>2024-09-24T20:20:52.210217</td>
    </tr>
    <tr>
      <th>2</th>
      <td>75 min</td>
      <td>4500</td>
      <td>587</td>
      <td>587051.00</td>
      <td>kj</td>
      <td>kj</td>
      <td>2024-03-09T07:27:46.642128</td>
    </tr>
    <tr>
      <th>3</th>
      <td>90 min</td>
      <td>5400</td>
      <td>1554</td>
      <td>1553594.02</td>
      <td>kj</td>
      <td>kj</td>
      <td>2024-09-01T20:10:55.379911</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5 min</td>
      <td>300</td>
      <td>71</td>
      <td>71090.35</td>
      <td>kj</td>
      <td>kj</td>
      <td>2021-06-27T09:48:37</td>
    </tr>
  </tbody>
</table>
</div>




```python
df_streaks = pd.DataFrame([response_json['streaks']])
df_streaks
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
      <th>current_weekly</th>
      <th>best_weekly</th>
      <th>start_date_of_current_weekly</th>
      <th>current_daily</th>
      <th>start_date_of_current_daily</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>114</td>
      <td>111</td>
      <td>1669792908</td>
      <td>0</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>




```python
df_achievements =  pd.DataFrame(response_json['achievement_counts']['achievements'])
achievement_template_norm = pd.json_normalize(df_achievements['template'])
df_achievements = pd.concat([df_achievements.drop(columns=['template']), achievement_template_norm], axis=1)

df_achievements.sort_values('count', ascending = False).head(10)
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
      <th>118</th>
      <td>302</td>
      <td>657e50c747d6458480f1ba6a0fa94c6a</td>
      <td>Dynamic Duo</td>
      <td>two_to_tango</td>
      <td>https://s3.amazonaws.com/peloton-achievement-i...</td>
      <td>Awarded for working out with a friend.</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>121</th>
      <td>208</td>
      <td>3a9ea8169d17455c86b9f52b1011e57b</td>
      <td>Squad</td>
      <td>socialite</td>
      <td>https://s3.amazonaws.com/peloton-achievement-i...</td>
      <td>Awarded for working out with 5 friends.</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>120</th>
      <td>177</td>
      <td>f0bdc95051b64c5bbd296e20d3fecb03</td>
      <td>Pack</td>
      <td>3_squad</td>
      <td>https://s3.amazonaws.com/peloton-achievement-i...</td>
      <td>Awarded for working out with 3 friends.</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>119</th>
      <td>165</td>
      <td>1b0f7ba0b9e945e88c93792484995c00</td>
      <td>Three's Company</td>
      <td>threes_company</td>
      <td>https://s3.amazonaws.com/peloton-achievement-i...</td>
      <td>Awarded for working out with 2 friends.</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>122</th>
      <td>114</td>
      <td>7a68d49d95ce4918b7408b26f91d9eac</td>
      <td>Flock</td>
      <td>10_flock</td>
      <td>https://s3.amazonaws.com/peloton-achievement-i...</td>
      <td>Awarded for working out with 10 friends.</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>207</th>
      <td>98</td>
      <td>df98e7119e4b478ea02494f22c004fe6</td>
      <td>Movement Tracker Gold</td>
      <td>movement_tracker_gold</td>
      <td>https://s3.amazonaws.com/peloton-achievement-i...</td>
      <td>Awarded for getting Movement Tracker credit fo...</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>0</th>
      <td>93</td>
      <td>bac5aefabb2940ba8f0a170fc9d63bf0</td>
      <td>Best Output</td>
      <td>best_output</td>
      <td>https://s3.amazonaws.com/peloton-achievement-i...</td>
      <td>Personal best output in a workout.</td>
      <td>None</td>
      <td>None</td>
    </tr>
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
      <th>29</th>
      <td>42</td>
      <td>4036702255e84f26bee944331ef92310</td>
      <td>Artist Series</td>
      <td>artist_series</td>
      <td>https://s3.amazonaws.com/peloton-achievement-i...</td>
      <td>Awarded for participating in an Artist Series ...</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>123</th>
      <td>38</td>
      <td>7bbfe8e58f6744b696b104acf2ecaa72</td>
      <td>Swarm</td>
      <td>20_swarm</td>
      <td>https://s3.amazonaws.com/peloton-achievement-i...</td>
      <td>Awarded for working out with 20 friends.</td>
      <td>None</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>



## Step 3. Data Type Coersion

As we review the dataframe, there are common data type issues that makes it harder for us to "read" the data. All columns are passed as string, so we'll need to change types for date or numeric column. The date fields are passsed as UNIX, and will need to be converted to timstamp to be easily interpretable. 


```python
def coerce_columns(df, type_dict, date_format=None, date_unit = None):
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
  return df
```


```python
col_type_personal_records = {
    'slug':'int',
    'value':'int',
    'raw_value':'float',
    'workout_date': 'datetime'
}

df_personal_records = coerce_columns(df_personal_records, col_type_personal_records, date_unit = 'mixed')

df_personal_records.sort_values('slug').head(5)
```

    Error converting column workout_date to datetime: non convertible value 2024-05-06T09:57:46.552438 with the unit 'mixed', at position 0





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
      <th>value</th>
      <th>raw_value</th>
      <th>unit</th>
      <th>unit_slug</th>
      <th>workout_id</th>
      <th>workout_date</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>4</th>
      <td>5 min</td>
      <td>300</td>
      <td>71</td>
      <td>71090.35</td>
      <td>kj</td>
      <td>kj</td>
      <td>fbdc1a79aa3742aa93f72ab821bfdd53</td>
      <td>2021-06-27T09:48:37</td>
    </tr>
    <tr>
      <th>5</th>
      <td>10 min</td>
      <td>600</td>
      <td>148</td>
      <td>147537.31</td>
      <td>kj</td>
      <td>kj</td>
      <td>867b9f0e534f4eb99f8165fdb3a603ac</td>
      <td>2024-04-29T09:41:50.385748</td>
    </tr>
    <tr>
      <th>6</th>
      <td>15 min</td>
      <td>900</td>
      <td>173</td>
      <td>172514.45</td>
      <td>kj</td>
      <td>kj</td>
      <td>6a574765b50645688e574ecb485c119d</td>
      <td>2021-01-07T21:03:53</td>
    </tr>
    <tr>
      <th>7</th>
      <td>20 min</td>
      <td>1200</td>
      <td>460</td>
      <td>460290.48</td>
      <td>kj</td>
      <td>kj</td>
      <td>b8a1fc94d9824a11b31927c44c76ac6e</td>
      <td>2024-09-08T11:46:38.416654</td>
    </tr>
    <tr>
      <th>8</th>
      <td>30 min</td>
      <td>1800</td>
      <td>572</td>
      <td>571577.48</td>
      <td>kj</td>
      <td>kj</td>
      <td>7700367be5464034b64a2d405ab24c29</td>
      <td>2024-06-23T20:08:42.478000</td>
    </tr>
  </tbody>
</table>
</div>



## Next Walkthrough

We've successfully accessed the Peloton API and retrieved valuable data. But as we explore more endpoints, we'll likely encounter similar patterns in our code. Repeating the same code blocks for different API calls can quickly become tedious and inefficient.

In the next walkthrough, I'll transform some of our existing code into reusable functions, making our Peloton data exploration more efficient and enjoyable.
