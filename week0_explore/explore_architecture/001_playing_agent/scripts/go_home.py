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

    # We might not be at the start of the Chessboard, but let's try going east a few times to get to the Dirt Path,
    # or just look around.
    print("\nSending 'look' to see where we are...", flush=True)
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

    # Let's try going east repeatedly. If we are deep in the chessboard, we might need multiple easts.
    # Let's send a sequence of commands to get home.
    # We will send: e, e, e, e, e, s, s, s, s, s, look
    commands = ["e", "e", "e", "e", "e", "s", "s", "s", "s", "s", "look"]
    for cmd in commands:
        print(f"\nSending '{cmd}'...", flush=True)
        s.sendall(f"{cmd}\n".encode('utf-8'))
        time.sleep(0.5)
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
