import pandas as pd
import numpy as np
from datetime import timedelta
import pickle
from tensorflow import keras
from streamlit_folium import folium_static
import folium
import streamlit as st
import datetime
from gsheetsdb import connect
path = 'https://github.com/nikgeokar/Parking_Violation_Prediction/blob/master'



Project_Path='/Users/nickkarras/PycharmProjects/'
#model =  keras.models.load_model('/Users/nickkarras/PycharmProjects/ParkingViolationPrediction/DNN_Regressor')

#
def Get_Inputs(Date,Time,Covid,Holidays,temp,humidity):
    Year, Month, Day = Date.year, Date.month, Date.day
    if Covid == 'Yes':
        Covid = 1
    else:
        Covid = 0

    if Holidays == 'Yes':
        Holidays = 1
    else:
        Holidays = 0

    Month = int(Month)
    Day = int(Day)
    Data = [Day, Month, Year, Time, temp, humidity, Covid, Holidays]
    Data_Frame = pd.DataFrame([Data], columns=['Day', 'Month', 'Year', 'Time', 'temp', 'humidity', 'Covid', 'Holidays'])
    return Data_Frame

def Get_DayName_TimeInt(Data_Frame):
    Data_Frame['Date'] = Data_Frame['Year'].map(str) + '/' + Data_Frame['Month'].map(str) + '/' + Data_Frame['Day'].map(
        str)
    Data_Frame['Date'] = pd.to_datetime(Data_Frame['Date'])
    Data_Frame['Day_Name'] = Data_Frame['Date'].dt.day_name()
    Data_Frame['Date_Time'] = Data_Frame['Date'].map(str) + ' ' + Data_Frame['Time'].map(str)
    Data_Frame['Date_Time'] = pd.to_datetime(Data_Frame['Date_Time'])
    Data_Frame['Time_Int'] = (Data_Frame['Date_Time'] - Data_Frame['Date_Time'].dt.normalize()).dt.total_seconds()
    del Data_Frame["Date"]
    del Data_Frame["Date_Time"]
    del Data_Frame["Time"]
    return Data_Frame

def Get_TimeSlot_TimeDistance(Data_Frame):
    Time_Slots=[23400,27000,30600,34200,37800,41400,45000,48600,52200,55800,59400,63000,66600,70200,73800]
    Scan_List = Data_Frame.values.tolist()
    Real_Time_Slots = []
    Time_Distance = []
    for i in range(0, len(Scan_List)):
        Real_Time = Scan_List[i][8]
        Distances = []


        for j in range(0, len(Time_Slots)):
            Distances.append(abs(Time_Slots[j] - Real_Time))

        Slots = np.column_stack((Time_Slots, Distances))
        Slots = sorted(Slots, key=lambda x: x[1])
        Real_Time_Slots.append(Slots[0][0])
        Time_Distance.append(Slots[0][1])
    Data_Frame.insert(9, "Real_Time", Real_Time_Slots, True)
    Data_Frame.insert(10, "Time_Distance", Time_Distance, True)
    Data_Frame['Real_Time'] = Data_Frame['Real_Time'] / timedelta(days=1).total_seconds()
    Data_Frame['Time_Int'] = Data_Frame['Time_Int'] / timedelta(days=1).total_seconds()
    Data_Frame['Time_Distance'] = Data_Frame['Time_Distance'] / timedelta(days=1).total_seconds()
    return Data_Frame

def encode(data, col, max_val):
    data[col + '_Sin'] = np.sin(2 * np.pi * data[col]/max_val)
    return data

def Get_Sins(Data_Frame):
    List = Data_Frame.values.tolist()
    Week_Day = []
    Data_Frame = Data_Frame.drop(['Day_Name'], axis=1)
    Day_Name_To_Day_Slot = [['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                            [1, 2, 3, 4, 5, 6, 7]]
    for i in range(0, len(List)):
        for j in range(0, 7):
            if List[i][7] == Day_Name_To_Day_Slot[0][j]:
                Week_Day.append(Day_Name_To_Day_Slot[1][j])

    Data_Frame.insert(2, "Week_Day", Week_Day, True)
    Data_Frame = encode(Data_Frame, 'Week_Day', 7)
    Data_Frame['Month'] = Data_Frame['Month'].astype(int)
    Data_Frame['Day'] = Data_Frame['Day'].astype(int)
    Data_Frame = encode(Data_Frame, 'Month', 12)
    List = Data_Frame.values.tolist()
    Date_Sin = []
    Month_Sin_Rules = [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                       [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]]  # Κανόνες με τις μέρες που έχει ο κάθε μήνας
    for i in range(0, len(List)):
        for j in range(0, 12):
            if List[i][1] == Month_Sin_Rules[0][j]:
                Max = Month_Sin_Rules[1][j]
        sin = np.sin(2 * np.pi * List[i][0] / Max)
        Date_Sin.append(sin)
    Data_Frame.insert(2, "Date_Sin", Date_Sin, True)
    Data_Frame = Data_Frame.drop(['Week_Day'], axis=1)
    Data_Frame = Data_Frame.drop(['Month'], axis=1)
    Data_Frame = Data_Frame.drop(['Day'], axis=1)
    Data_Frame = Data_Frame.drop(['Year'], axis=1)
    Data_Frame = Data_Frame.drop(['Time_Int'], axis=1)

    return Data_Frame

def GetSlotDistance_Capacity():
    gsheet_url = "https://docs.google.com/spreadsheets/d/16puIRUasJX1NNWkxH3lsm2VjMgCMrZpbAd8KBhPAjXU/edit?usp=sharing"
    conn = connect()
    rows = conn.execute(f'SELECT * FROM "{gsheet_url}"')
    Distance_Data = pd.DataFrame(rows)
    #Distance_Data=pd.read_csv(Project_Path+ '/ParkingViolationPrediction/Data/Distance.csv',sep=',',index_col=0)
    #Column_Names=['Slot_id','ΟΔΟΣ','ΜΕΣΟ','ΑΠΟ','ΕΩΣ','Capacity','ΔΙΕΥΘΥΝΣΗ','Latitude','Longitude']
    Column_Names2=['Slot_id','Capacity']
    gsheet_url2 = "https://docs.google.com/spreadsheets/d/1Vy-RSXwVo5DQSAV2OGixEhQ7L6TJTX09rBxdq-sdpZM/edit?usp=sharing"
    conn2 = connect()
    rows2 = conn2.execute(f'SELECT * FROM "{gsheet_url2}"')
    Parking_Slots = pd.DataFrame(rows2)


    #Parking_Slots=pd.read_csv(Project_Path+ '/ParkingViolationPrediction/Data/Parkink_Slot_Proccesed.csv',sep=',', names=Column_Names)
    Parking_Slots2=Parking_Slots[Column_Names2]
    Distance_Data=Distance_Data.merge(Parking_Slots2, on='Slot_id')
    Slots=Distance_Data['Slot_id']
    Distance_Data = Distance_Data.drop(['Slot_id'], axis=1)
    return Slots,Distance_Data

def Get_Final_Dataset(Data_Frame,Distance_Data):
    Names=['Date_Sin', 'Covid', 'Holidays', 'Capacity', 'Week_Day_Sin',
       'Month_Sin', 'Time_Distance', 'Real_Time', 'temp', 'humidity',
       'Γενικό_Νοσοκομείο_Θεσσαλονίκης', 'Λιμάνι',
       'Δημαρχείο_Θεσσαλονίκης', 'Λευκός_Πύργος', 'Αγορά_Καπάνι', 'Λαδάδικα',
       'Πλατεία_Άθωνος', 'Πλατεία_Αριστοτέλους', 'Ροτόντα',
       'Πλατεία_Αγίας_Σοφίας', 'Πλατεία_Αντιγονιδών',
       'Μουσείο_Μακεδονικού_Αγώνα', 'Πλατεία_Ναυαρίνου', 'Πάρκο_ΧΑΝΘ',
       'Ιερός_Ναός_Αγίου_Δημητρίου', 'ΔΕΘ', 'ΑΠΘ',
       'Άγαλμα_Ελευθερίου_Βενιζέλου', 'Ρωμαϊκή_Αγορά_Θεσσαλονίκης']
    Data_Frame = pd.concat([Data_Frame] * 396, ignore_index=True)
    Data_Frame = pd.concat([Data_Frame, Distance_Data], axis=1, join='inner')
    Data_Frame=Data_Frame[Names]
    return Data_Frame

def Scaller(Data_Frame):
    import pickle

    # with open("Standar_Scaller.pkl", 'rb') as f:
    #     Standar_Scaller = pickle.load(f)
    with open('Parking_Violation_Prediction/Standar_Scaller.pkl', 'rb') as handle:
        Standar_Scaller = handle.read()
        #Standar_Scaller = pickle.load(open(constants.path+'Standar_Scaller.pkl', 'rb'))
    Data_Frame = Standar_Scaller.transform(Data_Frame)
    return Data_Frame

def Inverse_Normalization(Targets):
    Targets=(Targets-0.1)/0.8
    return Targets

def Get_Predictions(Data_Frame):
    Predictions = model.predict(Data_Frame)
    #Predictions = Inverse_Normalization(Predictions)
    PredictionsFinal = []
    Predictions = Predictions.flatten()
    for i in range(0, len(Predictions)):
        PredictionsFinal.append((Predictions[i]))
    return PredictionsFinal

def Get_Slots_Info(Predictions,Slots):
    Predictions=pd.DataFrame(Predictions, columns=['Predictions'])
    Predictions=Predictions.round(decimals=3)
    Slots=pd.DataFrame(Slots, columns=['Slot_id'])
    Predictions = Predictions.join(Slots)
    gsheet_url2 = "https://docs.google.com/spreadsheets/d/1Vy-RSXwVo5DQSAV2OGixEhQ7L6TJTX09rBxdq-sdpZM/edit?usp=sharing"
    conn2 = connect()
    rows2 = conn2.execute(f'SELECT * FROM "{gsheet_url2}"')
    Parking_Slots = pd.DataFrame(rows2)
    Parking_Slots=Parking_Slots.merge(Predictions, on='Slot_id')
    return Parking_Slots


def Creat_Map(Parking_Slots):
    Parking_Slots['Predictions']=Parking_Slots['Predictions']*100
    Latitude = Parking_Slots['Latitude'].values.tolist()
    Longitude = Parking_Slots['Longitude'].values.tolist()
    Illegality_Rate = Parking_Slots['Predictions'].values.tolist()
    Point_List = 'Κωδικός Τομέα: '+ Parking_Slots['Slot_id'].map(str) + '| Διέυθυνση: ' + Parking_Slots['ΟΔΟΣ'].map(str) + '  ' + Parking_Slots[
        'ΑΠΟ'].map(str) + '-' + Parking_Slots['ΕΩΣ'].map(str) + '|  Παραβατικότητα: ' + Parking_Slots['Predictions'].map('{:,.1f}%'.format)

    Map_Parking_Slots = folium.Map([40.632778, 22.946944], tiles="openstreetmap", zoom_start=15)
    for i in range(0, len(Latitude)):
        if Illegality_Rate[i] < 5:
            Color = "#33cc33"
        elif Illegality_Rate[i] >= 5 and Illegality_Rate[i] < 20:
            Color = "#47b82e"
        elif Illegality_Rate[i] >= 20 and Illegality_Rate[i] < 40:
            Color = "#5ca329"
        elif Illegality_Rate[i] >= 40 and Illegality_Rate[i] < 55:
            Color = "#b22e00"
        elif Illegality_Rate[i] >= 55:
            Color = "#ff0000"

        folium.CircleMarker(location=[Latitude[i], Longitude[i]],
                            radius=5,
                            popup=Point_List[i],
                            fill_color=Color, color='black', fill_opacity=1
                            ).add_to(Map_Parking_Slots)

    return Map_Parking_Slots

def Creat_Map2(Parking_Slots):
    Parking_Slots['Illegal_Slots'] = Parking_Slots['Predictions'] * Parking_Slots['Capacity']
    Illegal_Slots=Parking_Slots['Illegal_Slots'].values.tolist()
    Latitude = Parking_Slots['Latitude'].values.tolist()
    Longitude = Parking_Slots['Longitude'].values.tolist()
    Point_List = 'Κωδικός Τομέα: '+ Parking_Slots['Slot_id'].map(str) + '| Διέυθυνση: ' + Parking_Slots['ΟΔΟΣ'].map(str) + '  ' + Parking_Slots[
        'ΑΠΟ'].map(str) + '-' + Parking_Slots['ΕΩΣ'].map(str) + '|  Παράνομες Σταθμέυσεις: ' + Parking_Slots['Illegal_Slots'].map('{:,.1f}'.format)

    Map_Parking_Slots2 = folium.Map([40.632778, 22.946944], tiles="openstreetmap", zoom_start=15)
    for i in range(0, len(Latitude)):
        if Illegal_Slots[i] < 1:
            Color = "#33cc33"
        elif Illegal_Slots[i] >= 1 and Illegal_Slots[i] < 2:
            Color = "#47b82e"
        elif Illegal_Slots[i] >= 2 and Illegal_Slots[i] < 3:
            Color = "#5ca329"
        elif Illegal_Slots[i] >= 4 and Illegal_Slots[i] < 6:
            Color = "#b22e00"
        elif Illegal_Slots[i] >= 6:
            Color = "#ff0000"
        folium.CircleMarker(location=[Latitude[i], Longitude[i]],
                            radius=5,
                            popup=Point_List[i],
                            fill_color=Color, color='black', fill_opacity=1
                            ).add_to(Map_Parking_Slots2)

    return Map_Parking_Slots2

###############################################################################
st.write("Πρόβλεψη παραβατικότητας στο σύστημα ελεγχόμενης στάθμευσης THESi ")
Date = st.date_input("Ημερομηνία")
Time = st.time_input('Ώρα', datetime.time(00,14))
Covid = st.selectbox('Περίοδο κορονοϊού:',('Ναι','Όχι'),key="Covid")
Holidays = st.selectbox('Ημέρα δημόσιας αργίας:',('Όχι','Ναι'), key="Holidays")
temp = st.slider('Θερμοκρασία (°C)', -15, 50, 14,key="Τemperature")
humidity = st.slider('Υγρασία (%)', 0, 100, 48,key="Humidity")
Data_Frame=Get_Inputs(Date,Time,Covid,Holidays,temp,humidity)

if st.button('Πρόβλεψη ποσοστό παραβατικότητας ανά τομέα'):
    Data_Frame=Get_DayName_TimeInt(Data_Frame)
    Data_Frame=Get_TimeSlot_TimeDistance(Data_Frame)
    Data_Frame=Get_Sins(Data_Frame)
    Slots,Distance_Data=GetSlotDistance_Capacity()
    Data_Frame=Get_Final_Dataset(Data_Frame,Distance_Data)
    #Data_Frame.to_csv(Project_Path+ '/ParkingViolationPrediction/Data/456.csv')
    Data_Frame=Scaller(Data_Frame)
    Predictions=Get_Predictions(Data_Frame)
    Parking_Slots=Get_Slots_Info(Predictions,Slots)
    Map_Parking_Slots=Creat_Map(Parking_Slots)
    folium_static(Map_Parking_Slots)

if st.button('Πρόβλεψη παράνομα κατειλημμένων θέσεων'):
    Data_Frame=Get_DayName_TimeInt(Data_Frame)
    Data_Frame=Get_TimeSlot_TimeDistance(Data_Frame)
    Data_Frame=Get_Sins(Data_Frame)
    Slots,Distance_Data=GetSlotDistance_Capacity()
    Data_Frame=Get_Final_Dataset(Data_Frame,Distance_Data)
    Data_Frame=Scaller(Data_Frame)
    Predictions=Get_Predictions(Data_Frame)
    Parking_Slots=Get_Slots_Info(Predictions,Slots)
    Map_Parking_Slots2=Creat_Map2(Parking_Slots)
    folium_static(Map_Parking_Slots2)