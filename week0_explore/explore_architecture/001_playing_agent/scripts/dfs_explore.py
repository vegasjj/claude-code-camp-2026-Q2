import socket
import time
import sys
import re
import os

# Paths for files
WORLD_MD = "/workspaces/claude-code-camp-2026-Q2/week0_explore/explore_architecture/001_playing_agent/data/world.md"
PLAYER_MD = "/workspaces/claude-code-camp-2026-Q2/week0_explore/explore_architecture/001_playing_agent/data/player.md"

ANSI_ESCAPE = re.compile(r'(?:\x1B[@-Z\\-_]|\x1B\[[0-?]*[ -/]*[@-~])')
PROMPT_RE = re.compile(r'(\d+)H\s+(\d+)M\s+(\d+)V')

OPPOSITE = {
    'n': 's',
    's': 'n',
    'e': 'w',
    'w': 'e',
    'u': 'd',
    'd': 'u',
}

def strip_ansi(text):
    return ANSI_ESCAPE.sub('', text)

def parse_room_info(clean_output):
    lines = [line.strip() for line in clean_output.split('\n') if line.strip()]
    room_name = None
    description_lines = []
    exits = []
    contents = []
    
    exits_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('[ Exits:') or line.startswith('[Exits:'):
            exits_idx = i
            match = re.search(r'\[\s*Exits:\s*([^\]]+)\]', line)
            if match:
                exits = match.group(1).strip().split()
            break
            
    if exits_idx != -1:
        valid_lines = []
        for line in lines[:exits_idx]:
            if line.startswith('>>>') or line.startswith('Welcome') or line.endswith('>'):
                continue
            valid_lines.append(line)
            
        if valid_lines:
            room_name = valid_lines[0]
            description_lines = valid_lines[1:]
            
        # Lines after exits_idx are contents (mobs, items, etc.)
        for line in lines[exits_idx + 1:]:
            if not PROMPT_RE.search(line) and not line.endswith('>'):
                contents.append(line)
    
    return room_name, " ".join(description_lines), exits, contents

def parse_player_state(clean_output):
    match = PROMPT_RE.search(clean_output)
    if match:
        return {
            'hp': match.group(1),
            'mana': match.group(2),
            'move': match.group(3)
        }
    return None

def update_files(visited_rooms, current_room_name, player_state):
    # Update player.md
    with open(PLAYER_MD, 'w') as f:
        f.write("# Player State\n\n")
        f.write(f"- **Name**: dummy\n")
        if player_state:
            f.write(f"- **HP**: {player_state.get('hp')}\n")
            f.write(f"- **Mana**: {player_state.get('mana')}\n")
            f.write(f"- **Move**: {player_state.get('move')}\n")
        f.write(f"- **Location**: {current_room_name}\n")

    # Update world.md
    with open(WORLD_MD, 'w') as f:
        f.write("# Midgaard World Map\n\n")
        f.write(f"Total discovered rooms: {len(visited_rooms)}\n\n")
        for room_key, info in visited_rooms.items():
            f.write(f"## {info['name']}\n")
            f.write(f"- **Description**: {info['description']}\n")
            f.write(f"- **Exits**: {', '.join(info['exits'])}\n")
            if info['contents']:
                f.write(f"- **Contents**:\n")
                for c in info['contents']:
                    f.write(f"  - {c}\n")
            f.write("\n")

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

def send_cmd(s, cmd):
    s.sendall(f"{cmd}\n".encode('utf-8'))
    _, raw_output = wait_for(s, [">"], timeout=3)
    return strip_ansi(raw_output)

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 4000))
    s.setblocking(False)

    # 1. Login
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

    # Initial look
    raw_output = send_cmd(s, "look")
    
    room_name, description, exits, contents = parse_room_info(raw_output)
    player_state = parse_player_state(raw_output)
    
    visited_rooms = {}
    
    # DFS Function
    def dfs(r_name, r_desc, r_exits, r_contents, depth=0, max_depth=15):
        nonlocal player_state
        if depth > max_depth:
            return False

        room_key = (r_name, r_desc)
        if room_key in visited_rooms:
            return False
            
        print(f"{'  ' * depth}DFS Visiting: {r_name} (depth {depth})")
        
        # Add to visited
        visited_rooms[room_key] = {
            'name': r_name,
            'description': r_desc,
            'exits': r_exits,
            'contents': r_contents
        }
        
        update_files(visited_rooms, r_name, player_state)

        # Check if this is the bakery
        if r_name and "bakery" in r_name.lower():
            print(f"\n*** FOUND BAKERY: {r_name} ***")
            # Get the menu using 'list'
            menu_output = send_cmd(s, "list")
            print("=== BAKERY MENU ===")
            print(menu_output)
            print("===================")
            # Write a marker file so the parent agent knows we found it
            with open("/home/codespace/.gemini/antigravity-cli/brain/96e2c461-eea3-4898-8c47-f4f95f09f649/scratch/bakery_menu.txt", "w") as mf:
                mf.write(f"Bakery Room Name: {r_name}\n")
                mf.write("Menu:\n")
                mf.write(menu_output)
            return True

        for direction in r_exits:
            if direction not in OPPOSITE:
                continue
                
            # Try to move in this direction
            print(f"{'  ' * (depth+1)}Moving {direction}...")
            move_output = send_cmd(s, direction)
            
            # Check if move succeeded
            next_name, next_desc, next_exits, next_contents = parse_room_info(move_output)
            
            # If room name and description are the same, or we didn't get exits, move failed or stayed in same room
            if (next_name == r_name and next_desc == r_desc) or not next_exits:
                print(f"{'  ' * (depth+1)}Move {direction} failed.")
                continue
                
            # If the next room is already visited, backtrack immediately
            next_key = (next_name, next_desc)
            if next_key in visited_rooms:
                print(f"{'  ' * (depth+1)}Room {next_name} already visited. Backtracking...")
                send_cmd(s, OPPOSITE[direction])
                continue
                
            # Update player state
            p_state = parse_player_state(move_output)
            if p_state:
                player_state = p_state
                
            # Recurse
            found = dfs(next_name, next_desc, next_exits, next_contents, depth + 1, max_depth)
            if found:
                return True
                
            # Backtrack
            print(f"{'  ' * (depth+1)}Backtracking {OPPOSITE[direction]}...")
            back_output = send_cmd(s, OPPOSITE[direction])
            back_name, back_desc, _, _ = parse_room_info(back_output)
            if back_name != r_name:
                print(f"WARNING: Backtracking failed! Expected {r_name}, got {back_name}")
                
        return False

    dfs(room_name, description, exits, contents)
    s.close()

if __name__ == '__main__':
    main()
