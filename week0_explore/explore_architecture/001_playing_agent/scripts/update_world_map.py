import re

WORLD_MD = "/workspaces/claude-code-camp-2026-Q2/week0_explore/explore_architecture/001_playing_agent/data/world.md"

new_rooms = """
## The Temple Square
- **Description**: You are standing on the temple square.  Huge marble steps lead up to the temple gate.  The entrance to the Clerics' Guild is to the west, and the old Grunting Boar Inn, is to the east.  Just south of here you see the market square, the center of Midgaard.
- **Exits**: n, e, s, w
- **Contents**:
  - A large fountain carved from blue-streaked marble is here, bubbling merrily.

## Market Square
- **Description**: You are standing on the market square, the famous Square of Midgaard. A large, peculiar looking statue is standing in the middle of the square. Roads lead in every direction, north to the temple square, south to the common square, east and westbound is the main street.
- **Exits**: n, e, s, w
- **Contents**:
  - An odif yltsaeb is here, walking backwards.

## Main Street
- **Description**: You are on the main street passing through the City of Midgaard.  South of here is the entrance to the Armory, and the bakery is to the north.  East of here is the market square.
- **Exits**: n, e, s, w
- **Contents**:
  - A Peacekeeper is standing here, ready to jump in at the first sign of trouble.
  - A cityguard stands here.

## The Bakery
- **Description**: You are standing inside the small bakery.  A sweet scent of danish and fine bread fills the room.  The bread and Danish are arranged in fine order on the shelves, and seem to be of the finest quality. A small sign is on the counter.
- **Exits**: s
- **Contents**:
  - The baker looks at you calmly, wiping flour from his face with one hand.
"""

def main():
    with open(WORLD_MD, 'r') as f:
        content = f.read()

    # Update Total discovered rooms
    match = re.search(r'Total discovered rooms: (\d+)', content)
    if match:
        old_count = int(match.group(1))
        new_count = old_count + 4
        content = re.sub(r'Total discovered rooms: \d+', f'Total discovered rooms: {new_count}', content)
    
    # Append new rooms
    content = content.strip() + "\n" + new_rooms.strip() + "\n"
    
    with open(WORLD_MD, 'w') as f:
        f.write(content)
        
    print("world.md updated successfully!")

if __name__ == '__main__':
    main()
