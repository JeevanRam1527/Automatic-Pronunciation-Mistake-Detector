import sqlite3

def init_sentences():
    """
    Initializes the sentences table with popular quotes from Harry Potter and Avengers.
    Populates the sentences for different difficulty levels.
    """
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS sentences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            difficulty TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')

    # Define the sentences
    easy_sentences = [
        "I solemnly swear that I am up to no good.",
        "I am Iron Man.",
        "I can do this all day.",
        "I’m always angry.",
        "I love you 3000.",
        "We have a Hulk.",
        "There’s no place like home.",
        "Wingardium Leviosa!",
        "Avengers assemble!",
        "Mischief managed.",
        "I can fly!",
        "Hulk smash!",
        "Expecto Patronum!",
        "To infinity and beyond!" # (Oops, wrong universe, let's keep it HP/Marvel)
        "Accio Firebolt!",
        "I am Groot.",
        "Alohomora!",
        "Wakanda Forever!",
        "Nitwit! Blubber! Oddment! Tweak!",
        "I am Steve Rogers.",
        "Yer a wizard, Harry.",
        "On your left.",
        "Turn to page 394.",
        "Part of the journey is the end.",
        "Anything’s possible if you’ve got enough nerve.",
        "I’m Mary Poppins, y’all!",
        "It matters not what someone is born, but what they grow to be.",
        "We are Groot.",
        "The mind is not a book, to be opened at will and examined at leisure.",
        "Whatever it takes."
    ]
    medium_sentences = [
        "It does not do to dwell on dreams and forget to live.",
        "Happiness can be found even in the darkest of times, if one only remembers to turn on the light.",
        "Fear of a name increases fear of the thing itself.",
        "Doth mother know you weareth her drapes?",
        "After all this time? Always.",
        "It is our choices, Harry, that show what we truly are, far more than our abilities.",
        "The hardest choices require the strongest wills.",
        "We must all face the choice between what is right and what is easy.",
        "I’m with you ‘til the end of the line.",
        "Words are, in my not-so-humble opinion, our most inexhaustible source of magic.",
        "Just because something works doesn’t mean it can’t be improved.",
        "Numbing the pain for a while will make it worse when you finally feel it.",
        "The truth is a beautiful and terrible thing, and should therefore be treated with great caution.",
        "Sometimes you gotta run before you can walk.",
        "If you want to know what a man’s like, take a good look at how he treats his inferiors, not his equals.",
        "Genius, billionaire, playboy, philanthropist.",
        "Understanding is the first step to acceptance, and only with acceptance can there be recovery.",
        "We are Groot.",
        "Curiosity is not a sin, but we should exercise caution with our curiosity.",
        "That’s my secret, Cap: I’m always angry.",
        "Time will not slow down when something unpleasant lies ahead.",
        "The city is flying and we’re fighting an army of robots. And I have a bow and arrow. None of this makes sense.",
        "It takes a great deal of bravery to stand up to our enemies, but just as much to stand up to our friends.",
        "I know what it’s like to lose. To feel so desperately that you’re right, yet to fail nonetheless.",
        "Things we lose have a way of coming back to us in the end, if not always in the way we expect.",
        "I’m putting together a team.",
        "Dark times lie ahead of us and there will be a time when we must choose between what is easy and what is right.",
        "I understood that reference.",
        "Every human life is worth the same, and worth saving.",
        "There are other ways to fight."
    ]
    hard_sentences = [
        "After all this time, we are still fighting for our lives. It’s not just a fight, it’s a war.",
        "A fight is not won by one person alone. It takes all of us to stand united.",
        "Magic will only carry you so far, but courage can move mountains.",
        "You don’t become what you are in a day, but you become who you choose to be each day.",
        "It is the unknown we fear when we look upon death and darkness, nothing more.",
        "Part of the journey is the end. What is grief, if not love persevering?",
        "This pain is part of being human…the fact that you can feel pain like this is your greatest strength.",
        "The measure of a person, of a hero, is how well they succeed at being who they are.",
        "Do not pity the dead, Harry. Pity the living, and, above all those who live without love.",
        "No amount of money ever bought a second of time.",
        "We’ve all got both light and dark inside us. What matters is the part we choose to act on. That’s who we really are.",
        "I know I’m asking a lot. But the price of freedom is high. It always has been. And it’s a price I’m willing to pay.",
        "Indifference and neglect often do much more damage than outright dislike.",
        "You get hurt, hurt 'em back. You get killed... walk it off.",
        "Youth cannot know how age thinks and feels. But old men are guilty if they forget what it was to be young.",
        "I can’t control their fear, only my own.",
        "The consequences of our actions are always so complicated, so diverse, that predicting the future is a very difficult business indeed.",
        "What is grief, if not love persevering?",
        "It is a curious thing, Harry, but perhaps those who are best suited to power are those who have never sought it.",
        "I’m not looking for forgiveness, and I’m way past asking for permission.",
        "To have been loved so deeply, even though the person who loved us is gone, will give us some protection forever.",
        "The world has changed, and none of us can go back. All we can do is our best, and sometimes the best that we can do is to start over.",
        "Differences of habit and language are nothing at all if our aims are identical and our hearts are open.",
        "I used to want to save the world. This beautiful place. But the closer you get, the more you see the great darkness within.",
        "It is important to fight and fight again, and keep fighting, for only then can evil be kept at bay though never quite eradicated.",
        "Compromise where you can. Where you can’t, don’t. Even if everyone is telling you that something wrong is something right.",
        "We must try not to sink beneath our anguish, but battle on.",
        "This universe is finite, its resources finite. If life is left unchecked, life will cease to exist. It needs correction.",
        "Let us step out into the night and pursue that flighty temptress, adventure.",
        "I finally rest. And watch the sun rise on a grateful universe."
    ]

    # Clear existing sentences first to ensure fresh data on each init
    c.execute("DELETE FROM sentences")

    # Insert the sentences into the database
    for s in easy_sentences:
        c.execute("INSERT INTO sentences (difficulty, content) VALUES (?, ?)", ("Easy", s))
    for s in medium_sentences:
        c.execute("INSERT INTO sentences (difficulty, content) VALUES (?, ?)", ("Medium", s))
    for s in hard_sentences:
        c.execute("INSERT INTO sentences (difficulty, content) VALUES (?, ?)", ("Hard", s))

    conn.commit()
    conn.close()

def get_random_sentence(difficulty):
    """
    Fetches a random sentence based on difficulty from the database.
    """
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT content FROM sentences WHERE difficulty=? ORDER BY RANDOM() LIMIT 1", (difficulty,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else "No sentence found."
