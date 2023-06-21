import pandas as pd
import numpy as np
import mysql.connector
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel
from dotenv import load_dotenv
import os

load_dotenv()


def get_recommendations(user, zone):
    df_user = pd.read_csv('Order_history.csv')
    df_rest = pd.read_csv('Rest_Info.csv')

    # user = 'User7'
    # zone = 'South'

    df_user = df_user[df_user['customer_id'] == user]

    df = df_user.merge(df_rest, on  = "rest_id", how= "left").sort_values(by= "order_id")
    
    # Get JDBC connection details from environment variables
    jdbc_host = os.getenv('MYSQL_HOST')
    jdbc_db = os.getenv('MYSQL_DB')
    jdbc_username = os.getenv('MYSQL_USERNAME')
    jdbc_password = os.getenv('MYSQL_PASSWORD')
    
    # Replace the placeholders with your MySQL connection details
    connection = mysql.connector.connect(
        host=jdbc_host,
        port = '3306',
        user=jdbc_username,
        password=jdbc_password,
        database=jdbc_db
    )
    cursor = connection.cursor()
    query = "SELECT * FROM pending_orders_table;"
    cursor.execute(query)
    result = cursor.fetchall()

    # convert SQL result to pandas dataframe and merge the restaurant info to the live restaurant data
    rest_live_df = pd.DataFrame(result, columns= ["rest_id", "pending_count"])
    del connection, cursor, query, result

    # filter by zone -- 'hard coded' right now but get from POST request
    rest_live_df = rest_live_df.merge(df_rest, on="rest_id", how = "left")
    rest_live_df = rest_live_df[rest_live_df['zone'] == zone]

    # one hot encoding categorical variables
    def encode_categorical(df, columns):
        return pd.get_dummies(df, columns=columns)

    user_orders_encoded = encode_categorical(df, ['cuisine'])
    rest_live_encoded = encode_categorical(rest_live_df, ['cuisine'])

    features = ['rating', 'budget', 'cuisine_indian', 'cuisine_italian', 'cuisine_mexican']

    user_features = user_orders_encoded[features].values
    rest_live_features = rest_live_encoded[features].values

    similarity_matrix = cosine_similarity(user_features, rest_live_features)
    similarity_df = pd.DataFrame(similarity_matrix, index=df.rest_id, columns=rest_live_df.index)

    ranked_restaurants = similarity_df.idxmax(axis=1).map(rest_live_df['rest_id'])
    ranked_restaurants = ranked_restaurants.reset_index().rename(columns = {'rest_id' : 'user_order_rest_id', 0 : 'similar_rest_id'})

    df_groupped = ranked_restaurants.groupby('similar_rest_id').count()
    df_groupped = df_groupped.rename(columns={'user_order_rest_id': 'count'})

    df_groupped['rank_similar'] = df_groupped['count'].rank(method='min', ascending=False)

    df_groupped = df_groupped.merge(rest_live_df, left_on="similar_rest_id", right_on = "rest_id", how = "left")

    df_groupped['rank_pending'] = df_groupped['pending_count'].rank(method='min', ascending=False)

    df_groupped['final_wt'] = (df_groupped['rank_pending'] * 0.2) + (df_groupped['rank_similar'] * 0.8)
    df_groupped['final_rank'] = df_groupped['final_wt'].rank(method='min', ascending=True)

    x = df_groupped.sort_values('final_rank', ascending = True).head(5)

    return x[['rest_name', 'cuisine', 'budget', 'rating']].reset_index(drop = True)