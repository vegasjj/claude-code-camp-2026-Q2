import socket
import time
import sys
import re

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 4000))
    s.setblocking(False)

    # Login
    def wait_for(strings):
        buffer = ""
        while True:
            try:
                data = s.recv(4096)
                if not data:
                    break
                chunk = data.decode('utf-8', errors='ignore')
                buffer += chunk
                for string in strings:
                    if string in buffer:
                        return string, buffer
            except BlockingIOError:
                time.sleep(0.05)

    wait_for(["By what name do you wish to be known?"])
    s.sendall(b"dummy\n")
    matched, _ = wait_for(["Password:", "Did I get that right"])
    if "Did I get that right" in matched:
        s.sendall(b"Y\n")
        wait_for(["Password:"])
    s.sendall(b"helloworld\n")
    wait_for(["*** PRESS RETURN:"])
    s.sendall(b"\n")
    wait_for(["Make your choice:"])
    s.sendall(b"1\n")
    wait_for([">"])

    # Move down
    s.sendall(b"d\n")
    wait_for([">"])
    s.sendall(b"look\n")
    _, raw = wait_for([">"])
    
    # Strip ANSI
    ansi_escape = re.compile(r'(?:\x1B[@-Z\\-_]|\x1B\[[0-?]*[ -/]*[@-~])')
    clean = ansi_escape.sub('', raw)
    print(clean)
    
    s.close()

if __name__ == '__main__':
    main()
