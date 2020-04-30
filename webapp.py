from app import app
import sys, getopt, json

def clear_file(file_name):
    with open(file_name, 'w') as filep:
        json.dump({}, filep)

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv, "c", ["clear"])
    except getopt.GetoptError:
        print('python webapp.py [-c or --clear for clearing memory]')
        sys.exit(2)
    for arg in args:
        if arg in ['-c','--clear']:
            clear_file('tx_history.json')
            clear_file('retired_store.json')
            clear_file('data_store.json')
            clear_file('purchase_request_store.json')
            print('Cleared memory')
    app.run(debug=True, host="127.0.0.1", port=8090)