import socket
import time
import sys
import re

ANSI_ESCAPE = re.compile(r'(?:\x1B[@-Z\\-_]|\x1B\[[0-?]*[ -/]*[@-~])')

def strip_ansi(text):
    return ANSI_ESCAPE.sub('', text)

def parse_room_info(clean_output):
    # Split by lines and remove empty lines
    lines = [line.strip() for line in clean_output.split('\n') if line.strip()]
    
    room_name = None
    description_lines = []
    exits = []
    
    # We find the exits line first
    exits_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('[ Exits:') or line.startswith('[Exits:'):
            exits_idx = i
            # Parse exits
            # e.g., "[ Exits: n e s w d ]"
            match = re.search(r'\[\s*Exits:\s*([^\]]+)\]', line)
            if match:
                exits = match.group(1).strip().split()
            break
            
    if exits_idx != -1:
        # The room name is usually the first line
        # But wait, there might be pre-room text (like news, MOTD, or command output).
        # To be safe, the room name is the line right after any welcome message, or we can look for
        # the line immediately preceding the description block.
        # Let's say lines before exits_idx that don't look like command echoing or other stuff.
        # Actually, if we just run 'look', the very first line of output is typically the room name.
        # Let's clean up any leading lines containing "Sending Command" or prompts.
        valid_lines = []
        for line in lines[:exits_idx]:
            if line.startswith('>>>') or line.startswith('Welcome') or line.endswith('>'):
                continue
            valid_lines.append(line)
            
        if valid_lines:
            room_name = valid_lines[0]
            description_lines = valid_lines[1:]
    else:
        # Exits not found, maybe not a room description
        pass
        
    return room_name, " ".join(description_lines), exits

def wait_for(s, strings, timeout=5):
    buffer = ""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            data = s.recv(4096)
            if not data:
                return None, buffer
            chunk = data.decode('utf-8', errors='ignore')
            buffer += chunk
            for string in strings:
                if string in buffer:
                    return string, buffer
        except BlockingIOError:
            time.sleep(0.05)
    return None, buffer

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 4000))
    s.setblocking(False)

    # Login sequence
    wait_for(s, ["By what name do you wish to be known?"])
    s.sendall(b"dummy\n")
    matched, _ = wait_for(s, ["Password:", "Did I get that right"])
    if "Did I get that right" in matched:
        s.sendall(b"Y\n")
        wait_for(s, ["Password:"])
    s.sendall(b"helloworld\n")
    wait_for(s, ["*** PRESS RETURN:"])
    s.sendall(b"\n")
    wait_for(s, ["Make your choice:"])
    s.sendall(b"1\n")
    wait_for(s, [">"])

    # Send look
    s.sendall(b"look\n")
    _, raw_output = wait_for(s, [">"])
    
    clean_output = strip_ansi(raw_output)
    print("=== RAW CLEAN OUTPUT ===")
    print(clean_output)
    print("========================")
    
    room_name, desc, exits = parse_room_info(clean_output)
    print(f"Room Name: {room_name}")
    print(f"Description: {desc}")
    print(f"Exits: {exits}")
    
    s.close()

if __name__ == '__main__':
    main()
