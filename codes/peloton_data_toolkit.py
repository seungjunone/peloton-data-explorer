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