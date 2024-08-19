import subprocess
import alpaca_request_methods

def model_trainer():
    alpaca_request_methods.fetch_stock_data()
    subprocess.run(['python', 'model_generator.py'])

def stock_predictor_using_pretrained_model():
    subprocess.run(['python', 'future_predictor.py'])
    probs = []
    with open('future_predictions.csv', 'r') as future_reader:
        lines = future_reader.readlines()
        count = 0
        for line in lines:
            if count > 0:
                line = line.split(',')
                symbol = line[0]
                probability_result = line[-1].split('\n')
                probability_result = int(probability_result[0])
                probs.append([symbol, probability_result])
            count += 1
        future_reader.close()

    return probs