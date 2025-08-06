import requests
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime

club_id = 2744
site_id = 2744
season = str(datetime.now().year)
api_token = st.secrets["api_token"]

@st.cache_data(ttl=3600) # Cache data for 1 hour (site reloads every 60 seconds)
def returnMatches(matchDate):
    #st.caption(f"Last data pull: {pd.Timestamp.now().strftime('%H:%M:%S')}")
    caption = (f"{pd.Timestamp.now().strftime('%H:%M:%S')}")

    url = "https://play-cricket.com/api/v2/matches.json"
    params = {
        "site_id": site_id,
        "season": season,
        "api_token": api_token
    }

    try:
        response = requests.get(url, params=params, verify=False)  # SSL verified by default
        response.raise_for_status()
        df = pd.DataFrame(response.json().get("matches", []))
        
        # Ensure match date is in datetime format
        df['match_date'] = pd.to_datetime(df['match_date'], errors='coerce', dayfirst=True)
        df = df.dropna(subset=['match_date'])  # Drop invalid dates

        # Filter by selected date
        filtered_df = df[df['match_date'].dt.date == matchDate]
        filtered_df['home_club_id'] = filtered_df['home_club_id'].astype(int)
        filtered_df['away_club_id'] = filtered_df['away_club_id'].astype(int)

        #club team
        filtered_df['my_team_name'] = np.where(
        filtered_df['home_club_id'] == club_id,
        filtered_df['home_team_name'],
        np.where(
            filtered_df['away_club_id'] == club_id,
            filtered_df['away_team_name'],
            None
        )
        )

        #club team id
        filtered_df['my_team_id'] = np.where(
        filtered_df['home_club_id'] == club_id,
        filtered_df['home_team_id'],filtered_df['away_team_id']
        )
  
        #oppo
        filtered_df['oppo_team_name'] = np.where(
        filtered_df['home_club_id'] == club_id,
        filtered_df['away_club_name'],
        np.where(
            filtered_df['away_club_id'] == club_id,
            filtered_df['home_club_name'],
            None
        )
        )

        #home away column
        filtered_df['venue'] = np.where(
        filtered_df['home_club_id'] == club_id,"H","A"
        )

        #club logo
        filtered_df['homelogo'] = np.where(
        filtered_df['home_club_id'] == club_id,"FCC",""
        )

        #club logo
        filtered_df['awaylogo'] = np.where(
        filtered_df['away_club_id'] == club_id,"FCC",""
        )

        #club logo
        filtered_df['home_team_name'] = np.where(
        filtered_df['home_club_id'] == club_id,filtered_df['home_team_name'],filtered_df['home_club_name']
        )

        #club logo
        filtered_df['away_team_name'] = np.where(
        filtered_df['away_club_id'] == club_id,filtered_df['away_team_name'],filtered_df['away_club_name']
        )

        filtered_df = filtered_df[['id', 'my_team_name', 'oppo_team_name', 'venue', 'my_team_id', 'home_team_name','away_team_name','homelogo','awaylogo', 'home_team_id','away_team_id','match_time']]

        return filtered_df, caption
    
    except Exception as e:
        return pd.DataFrame(), caption


@st.cache_data(ttl=55) # Cache data for 55 seconds (site reloads every 60 seconds)
def return_scores(filtered_df):

    caption = (f"{pd.Timestamp.now().strftime('%H:%M:%S')}")

    def get_match_detail(match_id):
        url = "https://play-cricket.com/api/v2/match_detail.json"
        params = {
            "match_id": match_id,
            "api_token": api_token
        }
        try:
            response = requests.get(url, params=params, verify=False)
            response.raise_for_status()
            match = response.json().get("match_details", [])[0] #to get results...
            innings = response.json().get("match_details", [])[0].get("innings", []) #to get scores...
            
            team1 = innings[0].get("team_batting_id") if len(innings) > 0 else None
            runs1 = innings[0].get("runs") if len(innings) > 0 else None
            wickets1 = innings[0].get("wickets") if len(innings) > 0 else None
            overs1 = innings[0].get("overs") if len(innings) > 0 else None
            
            team2 = innings[1].get("team_batting_id") if len(innings) > 1 else None
            runs2 = innings[1].get("runs") if len(innings) > 1 else None
            wickets2 = innings[1].get("wickets") if len(innings) > 1 else None
            overs2 = innings[1].get("overs") if len(innings) > 1 else None 

            result = match.get("result_description") if len(match) > 0 else None

            return pd.Series([team1, runs1, wickets1, overs1, team2, runs2, wickets2, overs2, result])
        except:
            st.warning(f"Failed to fetch details for match ID {match_id}.")
            return pd.Series([None]*9)
    
    try:

        filtered_df[['team1','runs1','wickets1','overs1','team2','runs2','wickets2','overs2','result']] = filtered_df['id'].apply(get_match_detail)
        #filtered_df['batting_team_1'] = filtered_df['id'].apply(get_match_detail)
        #details_df = pd.DataFrame(details)


        mask = filtered_df[['runs1', 'wickets1', 'overs1']].notna().all(axis=1)
        filtered_df['summary1'] = np.where(
        mask,
        filtered_df['runs1'].astype(str) + "/" +
        filtered_df['wickets1'].astype(str) + " in " +
        filtered_df['overs1'].astype(str) + " overs"
        , ""
        )       

        
        mask = filtered_df[['runs2', 'wickets2', 'overs2']].notna().all(axis=1)
        filtered_df['summary2'] = np.where(
        mask,
        filtered_df['runs2'].astype(str) + "/" +
        filtered_df['wickets2'].astype(str) + " in " +
        filtered_df['overs2'].astype(str) + " overs"
        , ""
        )   

        #home summary
        filtered_df['home_summary'] = np.where(
        filtered_df['home_team_id'].astype(int) == filtered_df['team1'].fillna(-1).astype(int),
        filtered_df['summary1'],filtered_df['summary2']
        )

        #away summary (during the first innings team2 is null)
        filtered_df['away_summary'] = np.where(
        filtered_df['away_team_id'].astype(int) == filtered_df['team1'].fillna(-1).astype(int),
        filtered_df['summary1'],filtered_df['summary2']
        )
        

        # Set result to 'Vs' if it's NaN or empty        
        filtered_df['match_time'] = filtered_df['match_time'].fillna('Vs')
        filtered_df['match_time'] = filtered_df['match_time'].replace('', 'Vs')
        filtered_df['result'] = filtered_df['result'].fillna(filtered_df['match_time'])
        filtered_df['result'] = np.where(
            filtered_df['result'] == '',
            filtered_df['match_time'],
            filtered_df['result']
        )
        #filtered_df['result'] = filtered_df['result'].replace('', filtered_df['match_time'])
        #filtered_df.loc[filtered_df['result'].isna() | (filtered_df['result'] == ""), 'result'] = 'Vs'
        
        #filtered_df['result'] = filtered_df['result'].fillna('Vs')
        # Merge with original match data on 'id'
        #filtered_df = pd.merge(filtered_df, details_df, on="id", how="left")
        #st.dataframe(filtered_df)
        
        filtered_df = filtered_df[['id', 'my_team_name', 'oppo_team_name', 'venue', 'my_team_id', 'home_summary', 'away_summary', 'result','homelogo','awaylogo','summary1','summary2','home_team_name','away_team_name']]
        
        return(filtered_df), caption

    #except requests.exceptions.SSLError:
    #    return "SSL error: certificate not trusted. Consider adding verify=False temporarily."
    except Exception as e:
        st.warning(f"{e}")
        filtered_df[['home_summary', 'away_summary', 'result']] = ""
        return filtered_df, caption
        
        #return pd.DataFrame(), caption
        # return (f"Error: {e}")
    


@st.cache_data(ttl=55) # Cache data for 55 seconds (site reloads every 60 seconds)
def return_scores2(filtered_df, matchDate):

    caption = (f"{pd.Timestamp.now().strftime('%H:%M:%S')}")

    url = "https://play-cricket.com/api/v2/result_summary.json"
    params = {
        "api_token": api_token,
        "season": season,
        "site_id": site_id,
        "from_match_date": matchDate,
        "end_match_date": matchDate
    }
    try:

        response = requests.get(url, params=params, verify=False)
        response.raise_for_status()
   
        df = pd.DataFrame(response.json().get("result_summary", []))
        #df = pd.json_normalize(response.json().get("result_summary", []))

        def extract_innings_scores(innings_list):
            try:
                team1 = innings_list[0]['team_batting_id'] if len(innings_list) > 0 else None
                runs1 = innings_list[0]['runs'] if len(innings_list) > 0 else None
                wickets1 = innings_list[0]['wickets'] if len(innings_list) > 0 else None
                overs1 = innings_list[0]['overs'] if len(innings_list) > 0 else None
                balls1 = innings_list[0]['balls'] if len(innings_list) > 0 else None

                team2 = innings_list[1]['team_batting_id'] if len(innings_list) > 1 else None
                runs2 = innings_list[1]['runs'] if len(innings_list) > 1 else None
                wickets2 = innings_list[1]['wickets'] if len(innings_list) > 1 else None
                overs2 = innings_list[1]['overs'] if len(innings_list) > 1 else None
                balls2 = innings_list[1]['balls'] if len(innings_list) > 1 else None

                return pd.Series([team1, runs1, wickets1, overs1, balls1, team2, runs2, wickets2, overs2, balls2])
            except Exception:
                return pd.Series([None]*10)

        df[['team1','runs1','wickets1','overs1','balls1','team2','runs2','wickets2','overs2','balls2']] = df['innings'].apply(extract_innings_scores)

        df = df[['id', 'result_description', 'team1', 'runs1', 'wickets1', 'overs1','balls1', 'team2', 'runs2', 'wickets2', 'overs2','balls2']]
        if 'id' in df.columns:
            filtered_df = filtered_df.merge(df, on='id', how='left')

        # balls used instead of overs in some games. coming through as decimals...
        filtered_df['balls1'] = filtered_df['balls1'].apply(
            lambda x: str(int(x)) if pd.notnull(x) and x != "" else ""
        )
        filtered_df['balls2'] = filtered_df['balls2'].apply(
            lambda x: str(int(x)) if pd.notnull(x) and x != "" else ""
        )

        mask = filtered_df[['runs1', 'wickets1', 'overs1']].notna().all(axis=1) & (filtered_df['runs1'] != '')
        filtered_df['format1'] = np.where(
            filtered_df['overs1'].astype(str) != '',
            filtered_df['overs1'].astype(str) + " overs",
            filtered_df['balls1'].astype(str) + " balls"
        )
        filtered_df['summary1'] = np.where(
        mask,
        filtered_df['runs1'].astype(str) + "/" +
        filtered_df['wickets1'].astype(str) + " in " +
        filtered_df['format1'].astype(str) #+ " overs"
        , ""
        )       

        
        mask = filtered_df[['runs2', 'wickets2', 'overs2']].notna().all(axis=1) & (filtered_df['runs2'] != '')
        filtered_df['format2'] = np.where(
            filtered_df['overs2'].astype(str) != '',
            filtered_df['overs2'].astype(str) + " overs",
            filtered_df['balls2'].astype(str) + " balls"
        )
        filtered_df['summary2'] = np.where(
        mask,
        filtered_df['runs2'].astype(str) + "/" +
        filtered_df['wickets2'].astype(str) + " in " +
        filtered_df['format2'].astype(str)
        , ""
        )   

        #home summary
        filtered_df['home_summary'] = np.where(
        filtered_df['home_team_id'].astype(int) == filtered_df['team1'].fillna(-1).astype(int),
        filtered_df['summary1'],filtered_df['summary2']
        )

        #away summary (during the first innings team2 is null)
        filtered_df['away_summary'] = np.where(
        filtered_df['away_team_id'].astype(int) == filtered_df['team1'].fillna(-1).astype(int),
        filtered_df['summary1'],filtered_df['summary2']
        )
        

        # Set result to 'Vs' if it's NaN or empty        
        filtered_df['match_time'] = filtered_df['match_time'].fillna('Vs')
        filtered_df['match_time'] = filtered_df['match_time'].replace('', 'Vs')
        filtered_df['result'] = filtered_df['result_description'].fillna(filtered_df['match_time'])
        filtered_df['result'] = np.where(
            filtered_df['result'] == '',
            filtered_df['match_time'],
            filtered_df['result']
        )

        filtered_df = filtered_df[['id', 'my_team_name', 'oppo_team_name', 'venue', 'my_team_id', 'home_summary', 'away_summary', 'result','homelogo','awaylogo','summary1','summary2','home_team_name','away_team_name']]
        
        return filtered_df, caption

    except Exception as e:
        #st.warning(f"{e}")
        filtered_df[['home_summary', 'away_summary']] = ""
        filtered_df['match_time'] = filtered_df['match_time'].fillna('Vs')
        filtered_df['match_time'] = filtered_df['match_time'].replace('', 'Vs')
        filtered_df['result'] = filtered_df['match_time']
        return filtered_df, caption
        
        #return pd.DataFrame(), caption
        # return (f"Error: {e}")




