import numpy as np
import pandas as pd
import datetime
from sklearn import preprocessing
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
def preprocessing_df(df,med_avg_by_drv=5, med_avg_of_drv=5):
    date1 = datetime.date(2014, 06, 01)

    ## Create a Churn column
    df["last_trip_date"] = pd.to_datetime(df["last_trip_date"])
    df["signup_date"] = pd.to_datetime(df["signup_date"])
    df["Churn"] = df["last_trip_date"] < date1

    ## Fill the NA in phone
    df["phone"] = df["phone"].fillna("Noninfo")

    ## Encode the object variable
    encoder_phone = preprocessing.LabelEncoder()
    encoder_city = preprocessing.LabelEncoder()
    df["phone"] = encoder_phone.fit_transform(df["phone"])
    df["city"] = encoder_city.fit_transform(df["city"])

    ## Fill NA for missing numerical values with provide median values
    df["avg_rating_by_driver"] = df["avg_rating_by_driver"].fillna(med_avg_by_drv)
    df["avg_rating_of_driver"] = df["avg_rating_of_driver"].fillna(med_avg_of_drv)

    return df

def plot_feat_importance(feature_importances,index):
    feat_scores = pd.DataFrame({"Mean Decrease Impurity" : feature_importances},
    index=index)
    feat_scores = feat_scores.sort_values(by="Mean Decrease Impurity")
    feat_scores.plot(kind="barh")

def standard_confusion_matrix(y_true, y_predict):
    y_true0 = np.array(y_true)
    y_predict0 = np.array(y_predict).reshape(y_true0.shape)
    tp = np.sum((y_true0 ==1).astype('int') * (y_predict0 == 1).astype("int"))
    tn = np.sum((y_true0 ==0).astype('int') * (y_predict0 == 0).astype("int"))
    fp = np.sum((y_true0 ==0).astype('int') * (y_predict0 == 1).astype("int"))
    fn = np.sum((y_true0 ==1).astype('int') * (y_predict0 == 0).astype("int"))
    return np.array([[tp, fp], [fn, tn]])

def profit_curve(cost_benefit,predicted_probs,labels):
    max_score = 0
    sort_index = np.argsort(predicted_probs)
    sort_index = sort_index[::-1]
    profits = []
    threshold_list = []
    threshold_list.append(1)
    y_pred = (predicted_probs > 1).astype("int")
    print(predicted_probs.shape, y_pred.shape, labels.shape)
    conf_mat = standard_confusion_matrix(labels, y_pred)
    profit = np.sum(conf_mat * cost_benefit) / float(np.sum(conf_mat))
    profits.append(profit)
    for i_ in sort_index:
        threshold = predicted_probs[i_]
        y_pred = (predicted_probs >= threshold).astype("int")
        score_ = accuracy_score(y_pred,labels)
        if (score_ > max_score):
            max_score = score_
        threshold_list.append(threshold)
        conf_mat = standard_confusion_matrix(labels, y_pred)
        profit = np.sum(conf_mat * cost_benefit) / float(np.sum(conf_mat))
        profits.append(profit)        
    print(max_score)
    print("The threshold to maximize profit is ", threshold_list[np.argmax(profits)])
    print("Max profit is ", max(profits))
    return profits, threshold_list
def plot_profit_curve(model,cost_benefit,X_train,X_test,y_train,y_test):
    model.fit(X_train,y_train)
    pred_prob = (model.predict_proba(X_test))[:, 0]
    profits, tem_= profit_curve(cost_benefit,pred_prob,y_test)
    percentages = np.arange(0, 100, 100. / len(profits))
    plt.plot(percentages, profits, label=model.__class__.__name__)
    plt.title("Profit Curve")
    plt.xlabel("Percentage of test instances (decreasing by score)")
    plt.ylabel("Profit")