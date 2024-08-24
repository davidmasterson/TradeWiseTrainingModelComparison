import subprocess
import alpaca_request_methods

# Global variable to hold the SocketIO instance
sio = None

def set_socketio_instance(socketio_instance):
    global sio
    sio = socketio_instance

def model_trainer():
    global sio
    percent = 90

    alpaca_request_methods.fetch_stock_data()
    sio.emit('update progress', {'percent':percent, 'type': 'model'})
    percent = 95
    subprocess.run(['python', 'Model_Training/model_generator.py'])
    
    percent = 100
    sio.emit('update progress', {'percent':percent, 'type':'model'})
    print('Emitted 100%')

def stock_predictor_using_pretrained_model():
    global sio
    percent = 0

    if sio is not None:
        sio.emit('update progress', {'percent':percent, 'type': 'prediction'})
        print("Emitted 10% progress")
    subprocess.run(['python', 'Future_Predictor/future_predictor.py'])
    percent = 5
    
    if sio is not None:
        sio.emit('update progress', {'percent':percent, 'type':'prediction'})
        print("Emitted 50% progress")
    
    probs = []
    percent = 50
    with open('Model_Training/future_predictions.csv', 'r') as future_reader:
        lines = future_reader.readlines()
        count = 0
        total_lines = len(lines) - 1
        

        def round_two_decimals(number):
            number = float(number)
            number = float("{:.2f}".format(number))
            return number
        
        for line in lines:
            if count > 0:
                line = line.split(',')
                symbol = line[0]
                purchase_date = line[1]
                purchase_price = round_two_decimals(line[2])
                sell_date = line[3]
                sell_price = line[4]
                days_to_sell = line[5]
                take_profit_price = round_two_decimals(line[6])
                stop_out_price = round_two_decimals(line[7])
                hit_take_profit = int(line[8])
                sector = line[9]
                SMA5_prob = round_two_decimals(line[10])
                SMA20_prob = round_two_decimals(line[11])
                SMA5_Slope_prob = round_two_decimals(line[12])
                SMA20_Slope_prob = round_two_decimals(line[13])
                open_mean = round_two_decimals(line[14])
                open_std = round_two_decimals(line[15])
                close_mean = round_two_decimals(line[16])
                close_std = round_two_decimals(line[17])
                SMA5_last = round_two_decimals(line[18])
                SMA20_last = round_two_decimals(line[19])
                SMA5_Slope_last = round_two_decimals(line[20])
                SMA20_Slope_last = round_two_decimals(line[21])
                symbol_encoded = int(line[22])
                purchase_date_encoded = int(line[23])
                sell_date_encoded = int(line[24])
                hit_take_profit_predicted = line[25].split('\n')
                hit_take_profit_predicted = int(hit_take_profit_predicted[0])
                probs.append([symbol,purchase_date,purchase_price,sell_date,sell_price,
                              days_to_sell,take_profit_price,stop_out_price,
                              hit_take_profit,sector,SMA5_prob,SMA20_prob,SMA5_Slope_prob,
                              SMA20_Slope_prob,open_mean,open_std,close_mean,close_std,SMA5_last,
                              SMA20_last,SMA5_Slope_last,SMA20_Slope_last,symbol_encoded,
                              purchase_date_encoded,sell_date_encoded,hit_take_profit_predicted])
            
            percent = 50 + int((count / total_lines) * 50)
            if sio is not None:
                sio.emit('update progress', {'percent':percent, 'type':'prediction'})
                print(f'emitted {percent} progress')
            
            count += 1
        future_reader.close()
    percent = 100
    if sio is not None:
        sio.emit('update progress', {'percent':percent, 'type':'prediction'})  # Emit 100% when done
        print("Emitted 100% progress")
    return probs