import os
import re
import socket
from http import HTTPStatus
import logging

logging.basicConfig(level=logging.DEBUG)


def create_response(request: str, raddr: tuple) -> str:
    '''
    Function for creating full response with status line, headers and body
    :param request: text of request
    :param raddr: tuple with client address
    :return: string of response
    '''

    # split request by rows
    request_list = request.split('\n')

    # get method as first word of the first row
    method = request_list[0].split()[0].strip()

    # get url as second word of the first row
    url = request_list[0].split()[1].strip()

    # create RegExpression pattern and find status
    pattern = re.compile('\?status=(\d+)', re.IGNORECASE)
    code = pattern.findall(url)

    # condition if status code is incorrect or not exists then Status_Code=200 OK
    if code:
        try:
            code = HTTPStatus(int(code[0]))
        except ValueError as e:
            code = HTTPStatus(200)
    else:
        code = HTTPStatus(200)

    # status
    status_line = f'HTTP/1.1 {code.value} {code.name}'

    # headers
    headers = 'Content-Type: text/html'

    # status + headers
    status_headers = '\r\n'.join([status_line, headers])

    # body
    body = [f'Request Method: {method}',
            f'Request source: {raddr}',
            f'Response status: {code.value} {code.name}']
    body += request_list[3:]
    body_list = ['<p>' + row.strip() + '</p>' for row in body]
    body = '\r\n'.join(body_list)

    # combine response
    response = '\r\n\r\n'.join([status_headers, body])
    logging.info(response)

    return response.encode('utf-8')


def start_server():
    '''
    Function to start echo server
    :return: None
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        srv_addr = ('', 5000)
        print(f'starting on {srv_addr}, pid: {os.getpid()}')

        s.bind(srv_addr)
        s.listen(5)

        while True:
            print('=====waiting for a connection======')
            conn, raddr = s.accept()
            print(s)
            print(conn)

            print('++++++connection from', raddr)
            while True:
                data = conn.recv(1024)
                text = data.decode('utf-8')
                print(f'received "{text}"')
                if text:
                    print('sending data back to the client')
                    conn.send(create_response(text, raddr))
                    conn.close()
                    break
                else:
                    print(f'no data from {raddr}')
                    conn.close()
                    break


if __name__ == '__main__':
    start_server()
