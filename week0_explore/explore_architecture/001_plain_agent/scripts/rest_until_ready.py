import socket
import time
import sys
import re

PROMPT_RE = re.compile(r'(\d+)H\s+(\d+)M\s+(\d+)V')

def parse_vigor(text):
    # Find the last occurrence of the prompt
    matches = list(PROMPT_RE.finditer(text))
    if matches:
        last_match = matches[-1]
        return int(last_match.group(3))
    return None

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 4000))
    s.setblocking(False)

    buffer = ""
    start_time = time.time()
    
    # Login
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

    # Get current vigor
    s.sendall(b"\n")
    time.sleep(0.5)
    
    initial_output = ""
    while True:
        try:
            data = s.recv(4096)
            if not data: break
            initial_output += data.decode('utf-8', errors='ignore')
        except BlockingIOError:
            break
            
    sys.stdout.write(initial_output)
    sys.stdout.flush()
    
    vigor = parse_vigor(initial_output)
    print(f"\nInitial Vigor parsed: {vigor}", flush=True)

    if vigor is None or vigor < 10:
        # We need to rest
        print("Vigor is low. Sitting down to rest...", flush=True)
        s.sendall(b"rest\n")
        time.sleep(0.5)
        
        while True:
            # Send a newline to get the prompt
            s.sendall(b"\n")
            time.sleep(1)
            
            # Read socket
            out = ""
            while True:
                try:
                    data = s.recv(4096)
                    if not data: break
                    out += data.decode('utf-8', errors='ignore')
                except BlockingIOError:
                    break
            
            if out:
                sys.stdout.write(out)
                sys.stdout.flush()
                v = parse_vigor(out)
                if v is not None:
                    print(f"\n[Vigor is now: {v}]", flush=True)
                    if v >= 15:
                        vigor = v
                        break
            
            print("Waiting for regeneration tick...", flush=True)
            time.sleep(5)

    # Stand up
    print("\nStanding up...", flush=True)
    s.sendall(b"stand\n")
    time.sleep(0.5)
    
    # Go down
    print("Moving down...", flush=True)
    s.sendall(b"d\n")
    time.sleep(0.5)
    
    # Read final output
    final_out = ""
    while True:
        try:
            data = s.recv(4096)
            if not data: break
            final_out += data.decode('utf-8', errors='ignore')
        except BlockingIOError:
            break
            
    sys.stdout.write(final_out)
    sys.stdout.flush()
    s.close()

if __name__ == '__main__':
    main()
