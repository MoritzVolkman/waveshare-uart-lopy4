import socket

def internet_connection(host='8.8.8.8', port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as e:
        print(e)
        return False

def main():
    print('Internet connection: ')
    if internet_connection():
        print('connected')
    else:
        print('not connected')
        
if __name__ == '__main__':
    main()