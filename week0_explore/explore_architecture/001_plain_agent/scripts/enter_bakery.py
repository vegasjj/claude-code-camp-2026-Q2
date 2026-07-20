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

    # We are currently at Main Street (East of market, or near it).
    # Let's send 'look' to see where we are.
    print("\nSending 'look'...", flush=True)
    s.sendall(b"look\n")
    time.sleep(0.5)
    
    look_out = ""
    while True:
        try:
            data = s.recv(4096)
            if not data: break
            look_out += data.decode('utf-8', errors='ignore')
        except BlockingIOError:
            break
            
    sys.stdout.write(look_out)
    sys.stdout.flush()

    # We need to reach the Main Street room that has the Bakery to its north.
    # That room is 1 West of Market Square.
    # If we are currently at "Main Street" (east of town, exits: n e s w):
    # From "The main street, to the north is the weapon shop...", Market Square is to the west.
    # So we go: w, w to get to Main Street (West of Market Square).
    # Let's send a list of movements to ensure we end up in the Bakery:
    # First, let's go 'w' until we hit Market Square, then go 'w' once more, then 'n'.
    # Actually, we can just send: w, w, w, n, look, list.
    # Let's check:
    # We are currently at the east main street.
    # w -> main street (west of that, general store to north)
    # w -> Market Square
    # w -> Main Street (Armory to south, Bakery to north)
    # n -> The Bakery
    commands = ["w", "w", "w", "n", "look", "list"]
    
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
