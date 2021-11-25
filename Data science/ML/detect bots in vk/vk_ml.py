import pandas as pd
import requests
import numpy as np
import csv
import time
import datetime
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt 
from sklearn.ensemble import ExtraTreesClassifier 
from sklearn.metrics import accuracy_score
import pprint
start_time = time.time()



# def checker(username):
#     response = requests.get('https://api.vk.com/method/users.get?',
#                                 params={
#                                         'access_token': token,
#                                         'v': version,
#                                         'user_ids': username
#                                     }
#                                     )
#     try:
#         user = response.json()['response']
#     except:
#         return None
#     return True
def features(username):
    username = username.replace('id', '')
    if any(c.isalpha() for c in username):
        username = str(username)
    try:
        username = username.split('https://vk.com/')[1]
    except:
        username = username

    token = ''
    version = '5.103'
    fields = [ "bdate, has_mobile, last_seen, connections, education, city, counters, has_photo,  fields, verified, personal, relatives, relation, schools, site, career, followers_count "]
    response = requests.get('https://api.vk.com/method/users.get?',
                                params={
                                        'access_token': token,
                                        'v': version,
                                        'user_ids': username
                                    }
                                    )
    try:
        user = response.json()['response']
    except:
        print("problem1")

    features = {}


    response = requests.get('https://api.vk.com/method/users.get?',
                            params={
                                    'access_token': token,
                                    'v': version,
                                    'user_ids': username,
                                    'fields': fields
                                }
                                )
    user = response.json()['response']
    # pprint.pprint(user)
    try:
        banned = user['deactivated']
    except:
        banned = None
    if banned:
        features = "banned"
        return features
    else:
        has_mobile = 0
        last_seen = 0
        links = 0
        education = 0
        city = 0
        has_photo = 0
        verified = 0
        personal = 0
        relatives = 0
        relation = 0
        closed = 1
        site = 0
        career = 0
        followers_count = 0
        closed = 0
        if user[0]['verified']:
            features = "verified"
            return features
        try:
            IsClosed = user[0]['is_closed']
        except:
            closed = 0
        if  IsClosed:
            try :
                has_photo = user['has_photo']
            except:
                has_photo = 0
            features = "private"
            return features
        else:   
            try:
                last_seen = user['last_seen']['time']
            except:
                last_seen = 0
            value = datetime.date.fromtimestamp(last_seen)
            today = datetime.date.today()
            # print(last_seen, value, today)
            diff = today - value
            # print(diff, diff.days)
            diff.days
            try :
                instagram = user[0]['instagram']
            except:
                instagram = None
            try :
                facebook = user[0]['facebook']
            except:
                facebook = None
            try :
                twitter = user[0]['twitter']
            except:
                twitter = None
            try :
                skype = user[0]['skype']
            except:
                skype = None
            try :
                study = user[0]['university_name']
            except:
                study = None
            try :
                school = user[0]['schools']
            except:
                school = None
            try:
                verified = user[0]['verified']
            except:
                verified = None
            try :
                has_photo = user[0]['has_photo']
            except:
                has_photo = 0

            try :
                city = user[0]['city']['title']
            except:
                city = None
            try:
                personal = user[0]['personal']
            except:
                personal = None
            try:
                relation = user[0]['relation']
            except:
                relation = None
            try:
                relatives = user[0]['relatives']
            except:
                relatives = None
            try:
                site = user[0]['site']
            except:
                site = None
            try:
                career = user[0]['career']
            except:
                career = None
            try:
                followers_count = user[0]['followers_count']
            except:
                followers_count = 358
            try:
                user[0]['can_access_closed']
            except:
                closed = 100
            if instagram or facebook or skype or twitter:
                links = 1
            else:
                links = 0
            if study or school:
                education = 1
            else:
                education = 0
            
            if personal or relation :
                personal = 1
            else:
                personal = 0
            if site :
                site = 1
            else:
                site = 0
            if career :
                career = 1
            else:
                career = 0
            if city:
                city = 1
            else:
                city = 0

            

            try :
                count_photos = user[0]['counters']['photos']
            except:
                count_photos = 0
            try :
                count_pages = user[0]['counters']['pages']
            except:
                count_pages = 0
            try :
                count_albums = user[0]['counters']['albums']
            except:
                count_albums = 0
            try :
                count_videos = user[0]['counters']['videos']
            except:
                count_videos = 0
            try :
                count_audios = user[0]['counters']['audios']
            except:
                count_audios = 0
            try :
                count_user_videos = user[0]['counters']['user_videos']
            except:
                count_user_videos = 0

            response = requests.get('https://api.vk.com/method/friends.get?',
            params={
                    'access_token': token,
                    'v': version,
                    'user_id': username
                }
                )
            try:
                count_user_friends = response.json()['response']['count']
            except:
                count_user_friends = 150
                
            
            # try :
            #     count_friends = count_user_friends['count']
            # except:
            #     count_friends = None







            features = {}

            features["IsCity"] = city
            features["IsProfile"] = personal
            features["IsLinks"] = links
            features["FriendCount"] = count_user_friends
            features["PhotoCount"] = count_photos
            features["PagesCount"] = count_pages
            features["FollowersCount"] = followers_count
            features["AlbumsCount"] = count_albums
            features["VideosCount"] = count_videos
            features["AudiosCount"] = count_audios
            features["OfflineDays"] = last_seen
            features["HasPhoto"] = has_photo
            features["Site"] = site
            features["Career"] = career
            features["Education"] = education

        # добавить соотношение друзья/подписчики
        try:
            features["following_followers_ratio"] = round(
                    count_user_friends / followers_count, 7)
        except ZeroDivisionError:
            features["following_followers_ratio"] = 2.8624688005235597

        # добавить соотношение друзья/фото
        try:
            features["following_photos_ratio"] = round(
                    count_user_friends / count_photos, 7)
        except ZeroDivisionError:
            features["following_photos_ratio"] = 48.6537926973262

        # добавить соотношение подписчики/фото
        try:
            features["followers_photos_ratio"] = round(
                followers_count / count_photos, 7)
        except ZeroDivisionError:
            features["followers_photos_ratio"] = 118.71968859411763
        return features


def read_data(name_dataset):
    dataset = pd.read_csv(name_dataset)  
    df = dataset.drop(['Url'], axis=1)
    y = df['rating']
    X = df.drop(['rating'], axis=1)
    X = X.to_numpy()
    y = y.to_numpy()
    return X, y

def new_data(name_dataset, sorted_values):
    dataset = pd.read_csv('dataset.csv')  
    df = dataset.drop(['Url'], axis=1)
    selected_features = []
    for i in sorted_values.keys():
        if sorted_values[i] > 0.020:
            selected_features.append(i)

    feature_dataset = dataset[selected_features]
    y = df['rating']
    X = df.drop(['rating'], axis=1)
    X = X.to_numpy()
    y = y.to_numpy()
    return X, y

def split_data(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
    return X_train, X_test, y_train, y_test

def classifier(X, y):
    clf = LinearDiscriminantAnalysis()
    clf.fit(X, y)
    return clf

def accuracy(clf, X_test, y_test):
    predicted =[]
    for i in X_test:
        predicted.append(clf.predict([i])) 
    print(predicted)
    # print("Точность составила: ", accuracy_score(y_test, predicted))
    return accuracy_score(y_test, predicted)

def features_importance(name_dataset):
    plt.figure(figsize=(10,15))
    # загрузка выборки
    df = pd.read_csv(name_dataset) 

    # удаление из выборки столбца классов
    df = df.drop('Url', axis = 1)
    y = df['rating'] 
    X = df.drop('rating', axis = 1) 
    # построение модели
    extra_tree_forest = ExtraTreesClassifier(n_estimators = 26, 
                                            criterion ='entropy', max_features = 2) 

    # тренировка модели
    extra_tree_forest.fit(X, y) 

    # подсчет важности признака
    feature_importance = extra_tree_forest.feature_importances_ 

    # Normalizing the individual importances 
    feature_importance_normalized = np.std([tree.feature_importances_ for tree in
                                            extra_tree_forest.estimators_], 
                                            axis = 0) 
    # print(len(feature_importance))
    features = ['IsCity','IsProfile','IsLinks','FriendCount','PhotoCount','PagesCount','FollowersCount','AlbumsCount','VideosCount','AudiosCount','OfflineDays','HasPhoto','Site','Career','Education','following_followers_ratio','following_photos_ratio','followers_photos_ratio']
    # print(len(features))
    font = {'family' : 'DejaVu Sans',
            'size'   : 15}
    plt.rc('font', **font)
    # Plotting a Bar Graph to compare the models 
    X = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'F13', 'F14', 'F15', 'F16', 'F17', 'F18']
    val = feature_importance_normalized

    heights = []

    barlist = plt.bar(X, val)
    for i in range(0,18):
        heights.append(barlist[i]._height)
        if barlist[i]._height > 0.020:
            barlist[i].set_color('r')

    values = {}        
    for i in range(len(heights)):
        values[features[i]] = heights[i]

    sorted_values = dict(sorted(values.items(), key=lambda item: item[1], reverse=True))
    for i in sorted_values.keys():
        print(i, sorted_values[i])
        
    plt.xlabel('Виды признаков') 
    plt.ylabel('Важность признака') 
    plt.title('Сравнение важности признаков') 
    plt.xticks(rotation=0)
    plt.show() 
    return sorted_values

def main():
    X, y = read_data('dataset.csv')
    X_train, X_test, y_train, y_test = split_data(X, y)
    clf = classifier(X_train, y_train)
    print('Точность исходная составила: ',accuracy(clf, X_test, y_test))

    values_features = features_importance('dataset.csv')
    X, y = new_data('dataset.csv', values_features)
    X_train, X_test, y_train, y_test = split_data(X, y)
    clf = classifier(X_train, y_train)
    print('Точность с новыми признаками составила: ',accuracy(clf, X_test, y_test))

def check_one(id):
    X, y = read_data('dataset.csv')
    X_train, X_test, y_train, y_test = split_data(X, y)
    clf = classifier(X_train, y_train)
    # print('Точность исходная составила: ',accuracy(clf, X_test, y_test))

    # values_features = features_importance('dataset.csv')
    # X, y = new_data('dataset.csv', values_features)
    # X_train, X_test, y_train, y_test = split_data(X, y)
    # clf = classifier(X_train, y_train)
    feat = features(id)
    features_list = list(feat.values())
    # print(clf.predict([features_list]))
    if clf.predict([features_list])[0] == 0:
        print("Бот")
    elif clf.predict([features_list])[0] == 1:
        print("Реальный пользователь")

if __name__ == '__main__':
    id = input("Введите ссылку на страницу пользователя: \n")

    # main()
    try:
        check_one(id)
    except:
        print("Невозможно получить данные о пользователе")