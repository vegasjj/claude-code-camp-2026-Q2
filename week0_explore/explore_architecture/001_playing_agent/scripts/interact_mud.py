import socket
import time
import sys

def interact():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 4000))
    s.setblocking(False)

    buffer = ""
    
    def wait_for(strings, timeout=10):
        nonlocal buffer
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                data = s.recv(4096)
                if not data:
                    print("\n[Disconnected]")
                    return None
                chunk = data.decode('utf-8', errors='ignore')
                sys.stdout.write(chunk)
                sys.stdout.flush()
                buffer += chunk
                for string in strings:
                    if string in buffer:
                        # Clear buffer up to the matched string to avoid re-matching
                        idx = buffer.index(string) + len(string)
                        buffer = buffer[idx:]
                        return string
            except BlockingIOError:
                time.sleep(0.1)
        return None

    # Wait for the name prompt
    print("Waiting for name prompt...")
    matched = wait_for(["By what name do you wish to be known?"])
    if not matched:
        print("Failed to get name prompt")
        return

    print("\nSending: dummy")
    s.sendall(b"dummy\n")

    # It might ask to confirm (if new user) or ask for password directly
    matched = wait_for(["Password:", "Did I get that right, dummy (Y/N)?", "Did I get that right, Dummy (Y/N)?"])
    if not matched:
        print("Failed after name")
        return

    if "Did I get that right" in matched:
        print("\nSending: Y")
        s.sendall(b"Y\n")
        matched = wait_for(["Password:"])
        if not matched:
            print("Failed to get password prompt after confirmation")
            return

    print("\nSending: helloworld")
    s.sendall(b"helloworld\n")

    # Let's wait to see if we logged in
    # MUD login success usually shows the MOTD or a command prompt
    # Let's just wait for a bit and see what it prints
    matched = wait_for(["\n*** Welcome to tbaMUD ***", "Welcome to the game", "reconnecting", "command", "\n\r", "\n"], timeout=5)
    
    # Send 'look'
    print("\nSending: look")
    s.sendall(b"look\n")
    
    # Read the response to 'look' and keep reading for 5 seconds
    wait_for(["NEVER_MATCH_THIS_STRING"], timeout=5)

    s.close()

if __name__ == '__main__':
    interact()
