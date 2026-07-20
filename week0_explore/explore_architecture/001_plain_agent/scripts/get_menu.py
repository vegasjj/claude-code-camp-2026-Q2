import socket
import time
import sys

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 4000))
    s.setblocking(False)

    buffer = ""
    start_time = time.time()
    
    while True:
        try:
            data = s.recv(4096)
            if not data:
                break
            chunk = data.decode('utf-8', errors='ignore')
            sys.stdout.write(chunk)
            sys.stdout.flush()
            buffer += chunk
            
            if "By what name do you wish to be known?" in buffer:
                s.sendall(b"dummy\n")
                buffer = ""
            elif "Did I get that right" in buffer:
                s.sendall(b"Y\n")
                buffer = ""
            elif "Password:" in buffer:
                s.sendall(b"helloworld\n")
                buffer = ""
            elif "already playing" in buffer or "already in the game" in buffer or "Reconnect?" in buffer:
                s.sendall(b"Y\n")
                buffer = ""
            elif "*** PRESS RETURN:" in buffer:
                s.sendall(b"\n")
                buffer = ""
            elif "Make your choice:" in buffer:
                s.sendall(b"1\n")
                buffer = ""
            elif buffer.strip().endswith(">"):
                break
        except BlockingIOError:
            time.sleep(0.05)
            if time.time() - start_time > 15:
                break

    # We should be in the Bakery now. Let's verify with 'look'.
    print("\nSending 'look'...", flush=True)
    s.sendall(b"look\n")
    time.sleep(0.5)
    while True:
        try:
            data = s.recv(4096)
            if not data: break
            sys.stdout.write(data.decode('utf-8', errors='ignore'))
            sys.stdout.flush()
        except BlockingIOError:
            break

    # Let's run 'list' and wait until we get a prompt
    print("\nSending 'list'...", flush=True)
    s.sendall(b"list\n")
    time.sleep(1.0)
    
    menu_output = ""
    start_read = time.time()
    while time.time() - start_read < 3:
        try:
            data = s.recv(4096)
            if not data:
                break
            chunk = data.decode('utf-8', errors='ignore')
            sys.stdout.write(chunk)
            sys.stdout.flush()
            menu_output += chunk
            if menu_output.strip().endswith(">"):
                break
        except BlockingIOError:
            time.sleep(0.1)

    s.close()

if __name__ == '__main__':
    main()
