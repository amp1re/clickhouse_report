import telegram
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import logging
import pandas as pd
import pandahouse
from read_db.CH import Getch
import os

sns.set()

connection = {
    'host': 'https://clickhouse.lab.karpov.courses',
    'password': 'dpo_python_2020',
    'user': 'student',
    'database': 'simulator_20220520'
}


def test_report(chat=None):
    chat_id = chat or 874505901
    bot = telegram.Bot(token='5348024464:AAFtNP9cWnRvcCkRolMEfzHZBgauOZBK34Y')

    start_q = 'SELECT '
    end_q = ' FROM simulator_20220520.feed_actions WHERE toDate(time) = today()-1;'

    dau = 'count(DISTINCT user_id) as "DAU"'
    views = 'countIf(user_id, action=\'view\') as "Количество просмотров"'
    likes = 'countIf(user_id, action=\'like\') as "Количество лайков"'
    ctr = 'countIf(user_id, action=\'like\') / countIf(user_id, action=\'view\') as "CTR"'
    posts_to_users = 'COUNT(post_id) / COUNT(DISTINCT user_id) AS "Соотношение постов к юзерам"'
    user_view = 'countIf(action=\'view\') / COUNT(DISTINCT user_id) AS "Просмотры на 1 юзера"'
    user_like = 'countIf(action=\'like\') / COUNT(DISTINCT user_id) AS "Лайки на 1 юзера"'

    indicators = [dau, views, likes, ctr, posts_to_users, user_view, user_like]
    indicator_list = []

    for indicator in indicators:
        q = start_q + indicator + end_q
        df = pandahouse.read_clickhouse(q, connection=connection)
        indicator_list.append(round(float(df.iloc[0][0]), 2))

    msg = (f"Данные за вчера: ") + "\n" \
          + (f"DAO: {indicator_list[0]}") + "\n" \
          + (f"Views: {indicator_list[1]}") + "\n" \
          + (f"Likes: {indicator_list[2]}") + "\n" \
          + (f"CTR: {indicator_list[3]}") + "\n" \
          + (f"Соотношение постов к юзерам: {indicator_list[4]}") + "\n" \
          + (f"Просмотры на 1 юзера: {indicator_list[5]}") + "\n" \
          + (f"Лайки на 1 юзера: {indicator_list[6]}")

    bot.sendMessage(chat_id=chat_id, text=msg)

    q = 'SELECT toStartOfDay(toDateTime(time)) AS "date", count(DISTINCT user_id) AS "unique users" FROM simulator_20220520.feed_actions WHERE toDate(time) BETWEEN today()-8 AND today()-1 GROUP BY toStartOfDay(toDateTime(time)) ORDER BY "unique users" DESC'
    df = pandahouse.read_clickhouse(q, connection=connection)
    x = df['date']
    y = df['unique users']
    sns.lineplot(x, y)
    plt.title('DAU')
    locs, labels = plt.xticks()
    plt.setp(labels, rotation=45)
    plot_object = io.BytesIO()
    plt.savefig(plot_object)
    plot_object.seek(0)
    plot_object.name = 'dau.png'
    plt.close()
    bot.sendPhoto(chat_id=chat_id, photo=plot_object)

    q = 'SELECT toStartOfDay(toDateTime(time)) AS "date", action, count(user_id) AS "количество" FROM simulator_20220520.feed_actions WHERE toDate(time) BETWEEN today()-8 AND today()-1 GROUP BY action, toStartOfDay(toDateTime(time))'
    df = pandahouse.read_clickhouse(q, connection=connection)
    ax = sns.lineplot(x='date', y='количество', data=df, hue='action')
    locs, labels = plt.xticks()
    plt.title('Views and Likes')
    locs, labels = plt.xticks()
    plt.setp(labels, rotation=45)
    plot_object = io.BytesIO()
    plt.savefig(plot_object)
    plot_object.seek(0)
    plot_object.name = 'views_and_likes.png'
    plt.close()
    bot.sendPhoto(chat_id=chat_id, photo=plot_object)

    q = 'SELECT toStartOfDay(toDateTime(time)) AS "date", countIf(user_id, action=\'like\') / countIf(user_id, action=\'view\') AS "CTR" FROM simulator_20220520.feed_actions WHERE toDate(time) BETWEEN today()-8 AND today()-1 GROUP BY toStartOfDay(toDateTime(time))'
    df = pandahouse.read_clickhouse(q, connection=connection)
    ax = sns.lineplot(x='date', y='CTR', data=df)
    locs, labels = plt.xticks()
    plt.title('CTR')
    locs, labels = plt.xticks()
    plt.setp(labels, rotation=45)
    plot_object = io.BytesIO()
    plt.savefig(plot_object)
    plot_object.seek(0)
    plot_object.name = 'ctr.png'
    plt.close()
    bot.sendPhoto(chat_id=chat_id, photo=plot_object)


try:
    test_report(-715060805)
except Exception as e:
    print(e)
