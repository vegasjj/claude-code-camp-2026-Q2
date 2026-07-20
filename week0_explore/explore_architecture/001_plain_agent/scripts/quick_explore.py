import socket
import time
import sys
import re

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 4000))
    s.setblocking(False)

    buffer = ""
    start_time = time.time()
    
    # Simple loop to read and reply based on what is in the buffer
    while True:
        try:
            data = s.recv(4096)
            if not data:
                print("Disconnected by server.", flush=True)
                break
            chunk = data.decode('utf-8', errors='ignore')
            sys.stdout.write(chunk)
            sys.stdout.flush()
            buffer += chunk
            
            # Check for prompts
            if "By what name do you wish to be known?" in buffer:
                print("\n[Sending username dummy]", flush=True)
                s.sendall(b"dummy\n")
                buffer = ""
            elif "Did I get that right" in buffer:
                print("\n[Sending Y for name confirmation]", flush=True)
                s.sendall(b"Y\n")
                buffer = ""
            elif "Password:" in buffer:
                print("\n[Sending password helloworld]", flush=True)
                s.sendall(b"helloworld\n")
                buffer = ""
            elif "already playing" in buffer or "already in the game" in buffer or "Reconnect?" in buffer:
                print("\n[Sending Y to reconnect]", flush=True)
                s.sendall(b"Y\n")
                buffer = ""
            elif "*** PRESS RETURN:" in buffer:
                print("\n[Pressing Return]", flush=True)
                s.sendall(b"\n")
                buffer = ""
            elif "Make your choice:" in buffer:
                print("\n[Selecting 1]", flush=True)
                s.sendall(b"1\n")
                buffer = ""
            elif buffer.strip().endswith(">"):
                print("\n[Logged In!]", flush=True)
                buffer = ""
                break
        except BlockingIOError:
            time.sleep(0.05)
            if time.time() - start_time > 15:
                print("\nTimeout waiting for login.", flush=True)
                break

    # Now we are logged in. Let's send 'look' to see where we are.
    s.sendall(b"look\n")
    time.sleep(0.5)
    # Read response
    while True:
        try:
            data = s.recv(4096)
            if not data:
                break
            sys.stdout.write(data.decode('utf-8', errors='ignore'))
            sys.stdout.flush()
        except BlockingIOError:
            break

    # Now go down
    print("\nSending 'd'...", flush=True)
    s.sendall(b"d\n")
    time.sleep(0.5)
    
    # Read response
    while True:
        try:
            data = s.recv(4096)
            if not data:
                break
            sys.stdout.write(data.decode('utf-8', errors='ignore'))
            sys.stdout.flush()
        except BlockingIOError:
            break

    s.close()

if __name__ == '__main__':
    main()
