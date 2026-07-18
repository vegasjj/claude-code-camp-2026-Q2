import socket
import time
import sys

def wait_for(s, strings, timeout=5):
    buffer = ""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            data = s.recv(4096)
            if not data:
                print("\n[Disconnected]")
                return None, buffer
            chunk = data.decode('utf-8', errors='ignore')
            sys.stdout.write(chunk)
            sys.stdout.flush()
            buffer += chunk
            for string in strings:
                if string in buffer:
                    return string, buffer
        except BlockingIOError:
            time.sleep(0.05)
    return None, buffer

def main():
    commands = sys.argv[1:] if len(sys.argv) > 1 else ["look"]
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 4000))
    s.setblocking(False)

    # 1. Wait for name prompt
    wait_for(s, ["By what name do you wish to be known?"])
    s.sendall(b"dummy\n")

    # 2. Wait for password or confirmation
    matched, _ = wait_for(s, ["Password:", "Did I get that right, dummy (Y/N)?", "Did I get that right, Dummy (Y/N)?"])
    if not matched:
        print("\nFailed during name phase")
        return
        
    if "Did I get that right" in matched:
        s.sendall(b"Y\n")
        wait_for(s, ["Password:"])
        
    s.sendall(b"helloworld\n")

    # 3. Wait for PRESS RETURN
    wait_for(s, ["*** PRESS RETURN:"])
    s.sendall(b"\n")

    # 4. Wait for choice prompt
    wait_for(s, ["Make your choice:"])
    s.sendall(b"1\n")

    # Wait for the game prompt to appear
    # Prompts in tbaMUD typically end with '>'
    wait_for(s, [">"])
    
    # 5. Execute commands sequentially
    for cmd in commands:
        print(f"\n>>> Sending Command: {cmd} <<<")
        s.sendall(f"{cmd}\n".encode('utf-8'))
        # Wait for the prompt again to ensure the command finished
        wait_for(s, [">"], timeout=3)
        time.sleep(0.5)

    # Done, close connection
    s.close()

if __name__ == '__main__':
    main()
