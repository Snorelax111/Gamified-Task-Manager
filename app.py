from flask import Flask, render_template, request, redirect, url_for, flash
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Initialize variables
tasks = []
points = 0
character = {
    'level': 1,
    'xp': 0,
    'stat_points': 0,
    'strength': 1,
    'attack_speed': 1,
    'defense': 1,
    'dexterity': 1,
    'hp': 100,
    'max_hp': 100,
    'equipment': {'weapon': None, 'armor': None},
    'coins': 0,
    'potions': {'Health Potion': 0, 'Strength Potion': 0, 'Speed Potion': 0}
}
equipment_rarity = ['Common', 'Uncommon', 'Rare', 'Epic', 'Legendary']

completed_tasks = {'low': 0, 'medium': 0, 'high': 0}

# Monster details (simplified)
base_monster = {'hp': 1, 'damage': 1, 'reward': 5}
monsters = []

# Boss Details
boss_index = 1

def reward_potion(priority):
    if priority == '3':  # Low Priority
        completed_tasks['low'] += 1
        if completed_tasks['low'] >= 10:
            completed_tasks['low'] = 0
            potion = random.choice(['Health Potion', 'Strength Potion', 'Speed Potion'])
            character['potions'][potion] += 1
            flash(f"You earned a {potion} for completing 10 low-priority tasks!", 'info')
    elif priority == '2':  # Medium Priority
        completed_tasks['medium'] += 1
        if completed_tasks['medium'] >= 5:
            completed_tasks['medium'] = 0
            potion = random.choice(['Health Potion', 'Strength Potion', 'Speed Potion'])
            character['potions'][potion] += 1
            flash(f"You earned a {potion} for completing 5 medium-priority tasks!", 'info')
    elif priority == '1':  # High Priority
        completed_tasks['high'] += 1
        if completed_tasks['high'] >= 2:
            completed_tasks['high'] = 0
            potion = random.choice(['Health Potion', 'Strength Potion', 'Speed Potion'])
            character['potions'][potion] += 1
            flash(f"You earned a {potion} for completing 2 high-priority tasks!", 'info')

def generate_monster(level):
    hp = base_monster['hp'] + (level * 5)
    damage = base_monster['damage'] + (level * 3)
    reward = base_monster['reward'] + level
    return {'name': f'Monster Level {level}', 'hp': hp, 'damage': damage, 'reward': reward}

def generate_boss(index):
    hp = 30 + (index * 30)
    damage = 15 + (index * 15)
    reward = 80 + (index * 20)
    color_intensity = index * 5  # Incrementally increase color intensity to match toughness of boss
    return {'name': f'Demon Lord {index}', 'hp': hp, 'damage': damage, 'reward': reward, 'color_intensity': color_intensity}

@app.route('/')
def index():
    if not monsters:
        monsters.append(generate_monster(character['level']))

    if len(monsters) < 2:  # Ensure the Demon Lord is always listed separately
        monsters.append(generate_boss(boss_index))

    high_priority_tasks = []
    medium_priority_tasks = []
    low_priority_tasks = []

    # Separate tasks by priority
    for task in tasks:
        if task['priority'] == '1':  # High Priority
            high_priority_tasks.append(task)
        elif task['priority'] == '2':  # Medium Priority
            medium_priority_tasks.append(task)
        else:  # Low Priority
            low_priority_tasks.append(task)

    # Combine the lists, starting with high priority
    sorted_tasks = high_priority_tasks + medium_priority_tasks + low_priority_tasks

    return render_template('index.html', tasks=sorted_tasks, points=points, character=character, monsters=monsters, boss_index=boss_index)

@app.route('/add_task', methods=['POST'])
def add_task():
    global points
    task = request.form.get('task')
    description = request.form.get('description')
    priority = request.form.get('priority')
    if task:
        tasks.append({
            'task': task,
            'description': description,
            'priority': priority,
            'completed': False
        })
    return redirect(url_for('index'))

@app.route('/complete_task/<int:task_id>')
def complete_task(task_id):
    global points
    if 0 <= task_id < len(tasks):
        task = tasks[task_id]
        if not task['completed']:
            task['completed'] = True
            points += 10
            character['xp'] += 10 * int(task['priority'])  # More XP for harder tasks
            reward_potion(task['priority'])  # Check and reward potions based on task priority
            check_level_up()
            get_chest(int(task['priority']))
    return redirect(url_for('index'))

@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if 0 <= task_id < len(tasks):
        del tasks[task_id]
    return redirect(url_for('index'))

@app.route('/reset')
def reset():
    global tasks, points, character, monsters, boss_index
    tasks = []
    points = 0
    monsters = []
    boss_index = 1  # Reset the boss index
    character = {
        'level': 1,
        'xp': 0,
        'stat_points': 0,
        'strength': 1,
        'attack_speed': 1,
        'defense': 1,
        'dexterity': 1,
        'hp': 100,
        'max_hp': 100,
        'equipment': {'weapon': None, 'armor': None},
        'coins': 0,
        'potions': {'Health Potion': 0, 'Strength Potion': 0, 'Speed Potion': 0}
    }
    return redirect(url_for('index'))

@app.route('/upgrade_stat/<string:stat>')
def upgrade_stat(stat):
    if character['stat_points'] > 0 and stat in character:
        character[stat] += 1
        character['stat_points'] -= 1
    return redirect(url_for('index'))

@app.route('/attack_monster/<int:monster_id>')
def attack_monster(monster_id):
    global monsters, boss_index
    if 0 <= monster_id < len(monsters):
        monster = monsters[monster_id]
        player_attack = character['strength'] * character['attack_speed']
        monster_hp = monster['hp']

        while monster_hp > 0 and character['hp'] > 0:
            # Player attacks first
            monster_hp -= player_attack
            if monster_hp <= 0:
                # Monster is defeated
                character['coins'] += monster['reward']
                if 'Demon Lord' in monster['name']:
                    boss_index += 1
                    if boss_index > 20:
                        flash("Congratulations! You have become disciplined!", 'success')
                        return redirect(url_for('reset'))
                    else:
                        flash(f"Victory! You defeated {monster['name']}! Prepare for the next challenge!", 'success')
                else:
                    flash(f"Victory! You defeated {monster['name']} and earned {monster['reward']} coins!", 'success')
                monsters = [generate_monster(boss_index)] + ([generate_boss(boss_index)] if boss_index <= 20 else [])
                return redirect(url_for('index'))

            # Monster attacks back if it's still alive
            if monster_hp > 0:
                damage_taken = max(monster['damage'] - character['defense'], 1)
                character['hp'] -= damage_taken

                # Check for dodge chance based on dexterity
                if random.random() < character['dexterity'] / 100:
                    flash("You dodged the monster's attack!", 'info')
                    character['hp'] += damage_taken  # Reverse damage if dodged

        if character['hp'] <= 0:
            # Player is defeated
            flash("You're too weak! You were defeated by the monster.", 'danger')
            character['hp'] = character['max_hp']  # Reset HP after defeat
        return redirect(url_for('index'))

@app.route('/use_potion/<string:potion>')
def use_potion(potion):
    if potion in character['potions'] and character['potions'][potion] > 0:
        character['potions'][potion] -= 1
        if potion == 'Health Potion':
            flash(f"You used a Health Potion! Your HP is restored. ", 'info')
            character['hp'] = character['max_hp']
        elif potion == 'Strength Potion':
            flash(f"You used a Strength Potion! Your strength is permanently increased. ", 'info')
            character['strength'] += 5  # Permanent boost
        elif potion == 'Speed Potion':
            flash(f"You used a Speed Potion! Your attack speed is permanently increased.", 'info')
            character['attack_speed'] += 1  # Permanently boost
    return redirect(url_for('index'))

def check_level_up():
    while character['xp'] >= character['level'] * 100:
        character['xp'] -= character['level'] * 100
        character['level'] += 1
        character['stat_points'] += 1
        flash("Level Up! You gained a stat point.", 'success')

def apply_stat_boost(equipment_type, rarity):
    boosts = {
        'Common': 1,
        'Uncommon': 2,
        'Rare': 3,
        'Epic': 5,
        'Legendary': 7
    }
    boost_value = boosts[rarity]

    if equipment_type == 'weapon':
        character['strength'] += boost_value
    elif equipment_type == 'armor':
        character['defense'] += boost_value
    elif equipment_type == 'helmet':
        character['dexterity'] += boost_value
    elif equipment_type == 'boots':
        character['attack_speed'] += boost_value

def get_chest(priority):
    chance = random.random()
    rarity = 'Common'
    if priority == 1:
        if chance > 0.95:  # 5% chance for Legendary
            rarity = 'Legendary'
        elif chance > 0.85:  # 10% chance for Epic
            rarity = 'Epic'
        elif chance > 0.65:  # 20% chance for Rare
            rarity = 'Rare'
        elif chance > 0.4:  # 25% chance for Uncommon
            rarity = 'Uncommon'
    elif priority == 2:
        if chance > 0.9:  # 10% chance for Epic
            rarity = 'Epic'
        elif chance > 0.7:  # 20% chance for Rare
            rarity = 'Rare'
        elif chance > 0.4:  # 30% chance for Uncommon
            rarity = 'Uncommon'
    else:  # Priority 3
        if chance > 0.8:  # 20% chance for Rare
            rarity = 'Rare'
        elif chance > 0.5:  # 30% chance for Uncommon
            rarity = 'Uncommon'

    equipment_type = random.choice(['weapon', 'armor', 'helmet', 'boots'])
    new_equipment = f"{rarity} {equipment_type.capitalize()}"
    character['equipment'][equipment_type] = new_equipment
    apply_stat_boost(equipment_type, rarity)  #applies stat boosts from equipments
    flash(f"You found a {new_equipment}! It boosts your {equipment_type}.", 'info') 

if __name__ == '__main__':
    app.run(debug=True)
