import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sklearn.model_selection import train_test_split
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
import csv

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

# print(color.BOLD + 'Hello World !' + color.END)

df = pd.read_csv("attack_test.csv")
# df.info()
with open("attack_test.csv", newline='') as f:
    reader = csv.reader(f)
    origin_X_test = list(reader)

num_feat = ['src_bytes','dst_bytes','wrong_fragment','urgent','hot','num_failed_logins','num_compromised','root_shell','su_attempted','num_root','num_file_creations','num_shells','num_access_files','num_outbound_cmds','count','srv_count','serror_rate','srv_serror_rate','rerror_rate','srv_rerror_rate','same_srv_rate','diff_srv_rate','srv_diff_host_rate','dst_host_count','dst_host_srv_count','dst_host_same_srv_rate','dst_host_diff_srv_rate','dst_host_same_src_port_rate','dst_host_srv_diff_host_rate','dst_host_serror_rate','dst_host_srv_serror_rate','dst_host_rerror_rate','dst_host_srv_rerror_rate']
#Change features with object or string value into numeric numbers
ord_feat = ['protocol_type', 'service', 'flag']
#Nom_feat = column value with 0 or 1
nom_feat = ['land', 'logged_in', 'is_host_login', 'is_guest_login']
num_feat = ['src_bytes','dst_bytes','wrong_fragment','urgent','hot','num_failed_logins','num_compromised','root_shell','su_attempted','num_root','num_file_creations','num_shells','num_access_files','num_outbound_cmds','count','srv_count','serror_rate','srv_serror_rate','rerror_rate','srv_rerror_rate','same_srv_rate','diff_srv_rate','srv_diff_host_rate','dst_host_count','dst_host_srv_count','dst_host_same_srv_rate','dst_host_diff_srv_rate','dst_host_same_src_port_rate','dst_host_srv_diff_host_rate','dst_host_serror_rate','dst_host_srv_serror_rate','dst_host_rerror_rate','dst_host_srv_rerror_rate']

#Scale the num, ord, nom datasets
X_test, y_test = df.drop(columns=['class'], axis = 1, inplace=False), df['class'].values
# print(X_test[1:2])

ohe = OneHotEncoder(sparse=False)
oe = OrdinalEncoder()
scalar = StandardScaler()

ohe.fit(X_test[nom_feat].values)
oe.fit(X_test[ord_feat].values)
#reshape Test dataset into 3d array

scalar.fit(X_test[num_feat].values)
X_test_nom = ohe.transform(X_test[nom_feat].values)
X_test_ord = oe.transform(X_test[ord_feat].values)
X_test_num = scalar.transform(X_test[num_feat].values)
X_test = np.concatenate([X_test_ord, X_test_num, X_test_nom], axis=1)

X_test = X_test.reshape((X_test.shape[0],1,X_test.shape[1]))
y_test = y_test.reshape((y_test.shape[0],1,1))

model = tf.keras.models.load_model("LSTM_DDoS_Detection.model")
# CATEGORIES = ["",""]

N = int(input("\n"+color.GREEN+"How many packets do you want to check? We have "+ color.RED + str(len(df)) + color.GREEN + " packets you can check: "+color.END))
count_ddos = 0

count_normal = 0
for i, each in enumerate(X_test):
    if i < N:
        each = each.reshape((each.shape[0],1,each.shape[1]))
        prediction = model.predict([each])
        scale_pred = prediction[0][0][0]
        if scale_pred >= 0.5:
            print(color.RED + "DDoS Packet found." + color.END )
            print(color.PURPLE + "Packet: "  + color.END + str(origin_X_test[i+2])+"\n")
            count_ddos += 1
        elif scale_pred < 0.5:
            print(color.GREEN + "This packet is a normal Packet." + color.END)
            print(color.PURPLE + "Packet: " + color.END + str(origin_X_test[i+2])+"\n")
            count_normal += 1
    else:
        print(color.YELLOW + str(count_normal) + color.GREEN + " Normal Packets Found." + color.END+"\n")
        print(color.YELLOW + str(count_ddos) + color.RED + " DDoS Packets Found." + color.END+"\n")
        break
