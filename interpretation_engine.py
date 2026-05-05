"""
DharmaPath Kundli Interpretation Engine
Rule-based Jyotish interpretation layer.

Input:
    result dictionary from KundliEngine.calculate_all()

Output:
    List of report sections:
    [
      {"title": "...", "paragraphs": ["...", "..."]},
      ...
    ]
"""

RASHI_NATURE = {
    "Mesha": "active, bold, direct, courageous and action-oriented",
    "Vrishabha": "stable, practical, persistent, comfort-loving and grounded",
    "Mithuna": "intellectual, communicative, flexible, curious and analytical",
    "Karka": "emotional, nurturing, protective, family-oriented and intuitive",
    "Simha": "confident, expressive, royal, leadership-oriented and proud",
    "Kanya": "analytical, disciplined, service-oriented, detail-focused and practical",
    "Tula": "balanced, diplomatic, artistic, relationship-oriented and refined",
    "Vrishchika": "intense, private, transformative, emotional and research-oriented",
    "Dhanu": "philosophical, dharmic, optimistic, spiritual and knowledge-seeking",
    "Makara": "disciplined, hardworking, practical, patient and responsibility-driven",
    "Kumbha": "innovative, humanitarian, unconventional, intellectual and future-oriented",
    "Meena": "spiritual, compassionate, imaginative, sensitive and devotional",
}

RASHI_DESCRIPTION = {
    "Mesha": (
        "Mesha (Aries) is the first sign of the zodiac, a cardinal fire sign governed by Mars. It embodies "
        "initiation, courage, and a pioneering spirit. There is boldness and enthusiasm in its expression, "
        "though impulsiveness may need to be consciously directed toward constructive ends."
    ),
    "Vrishabha": (
        "Vrishabha (Taurus) is a fixed earth sign ruled by Venus. It brings stability, patience, and a deep "
        "appreciation for beauty, comfort, and material security. There is sensuality, practicality, and "
        "groundedness in this sign. When pressed for change too quickly, a stubborn streak may surface."
    ),
    "Mithuna": (
        "Mithuna (Gemini) is a mutable air sign ruled by Mercury. It carries intellectual curiosity, "
        "communicative skill, and versatile adaptability. There is a love of ideas, information, and variety in "
        "expression. The mind is agile and quick, though scattered focus may arise when multiple interests "
        "compete for attention simultaneously."
    ),
    "Karka": (
        "Karka (Cancer) is a cardinal water sign ruled by the Moon. It brings emotional depth, nurturing instincts, "
        "and a strong connection to home and family. There is a natural empathy and a genuine desire to care for "
        "others. Emotional fluctuations may arise, yet this sign carries a profound inner strength rooted in "
        "feeling, memory, and belonging."
    ),
    "Simha": (
        "Simha (Leo) is a fixed fire sign ruled by the Sun. It bestows confidence, dignity, creativity, and a "
        "natural flair for self-expression and leadership. There is warmth and magnanimity in this sign, with an "
        "innate desire to shine and inspire. Pride is a defining quality — when well-directed, it becomes "
        "genuine greatness, generosity, and a gift for uplifting those around them."
    ),
    "Kanya": (
        "Kanya (Virgo) is a mutable earth sign ruled by Mercury. It imparts precision, analytical ability, and "
        "a deep commitment to service and continuous self-improvement. There is a strong desire to refine, "
        "organise, and contribute meaningfully. Critical thinking is a natural gift, though the tendency toward "
        "perfectionism may need to be balanced with patience and acceptance."
    ),
    "Tula": (
        "Tula (Libra) is a cardinal air sign ruled by Venus. It brings balance, diplomacy, aesthetic refinement, "
        "and a deep desire for harmonious relationships. There is a natural pursuit of fairness, beauty, and "
        "cooperation, with skill in navigating social dynamics gracefully. The ability to see multiple perspectives "
        "is a strength, though indecisiveness may arise when equally weighted options require a clear choice."
    ),
    "Vrishchika": (
        "Vrishchika (Scorpio) is a fixed water sign co-ruled by Mars and Ketu. It imparts intensity, depth, and "
        "transformative power. There is a natural inclination toward research, psychology, and hidden matters, "
        "with a focused determination to probe beneath the surface of experience. Resilience is extraordinary — "
        "the individual often emerges profoundly strengthened through deep inner change and transformation."
    ),
    "Dhanu": (
        "Dhanu (Sagittarius) is a mutable fire sign ruled by Jupiter. It carries optimism, philosophical inquiry, "
        "and a love of expansion and adventure. There is a natural inclination toward higher learning, spiritual "
        "exploration, and broad life experience. This sign is generous, idealistic, and freedom-loving, driven by "
        "a sincere quest for meaning, truth, and wisdom across diverse traditions."
    ),
    "Makara": (
        "Makara (Capricorn) is a cardinal earth sign ruled by Saturn. It brings discipline, ambition, patience, "
        "and a strong sense of duty and responsibility. There is a karmic quality to this sign — rewards come "
        "through consistent effort and integrity. Professional recognition and status are often significant "
        "life themes for those with placements here."
    ),
    "Kumbha": (
        "Kumbha (Aquarius) is a fixed air sign co-ruled by Saturn and Rahu. It imparts originality, humanitarian "
        "values, and a progressive, future-oriented perspective. There is a natural detachment that enables reform "
        "and original thinking. This sign is unconventional and independent, drawn to collective well-being and "
        "intellectual innovation, often ahead of its time."
    ),
    "Meena": (
        "Meena (Pisces) is a mutable water sign co-ruled by Jupiter and Ketu. It brings spiritual sensitivity, "
        "compassion, imagination, and a deep connection to the unseen dimensions of life. There is a natural "
        "openness to divine inspiration and selfless giving. A longing for transcendence and inner peace gently "
        "shapes the outlook of those with influences in this sign."
    ),
}

HOUSE_MEANINGS = {
    1: "self, personality, body, confidence, health and life direction",
    2: "wealth, speech, family, food habits, values and accumulated resources",
    3: "courage, communication, siblings, skills, effort and short journeys",
    4: "mother, home, property, inner peace, education and emotional foundation",
    5: "intelligence, children, creativity, mantra, past-life merit and learning",
    6: "service, disease, debts, enemies, competition, discipline and daily work",
    7: "marriage, spouse, partnerships, business agreements and public dealings",
    8: "longevity, transformation, hidden matters, occult, inheritance and sudden events",
    9: "dharma, fortune, father, guru, higher knowledge, pilgrimage and blessings",
    10: "career, karma, authority, profession, status and public life",
    11: "gains, income, friends, networks, ambitions and fulfillment of desires",
    12: "expenses, sleep, foreign lands, isolation, moksha, spirituality and surrender",
}

HOUSE_INTRO = {
    1: (
        "The 1st house represents the self, personality, physical presence, and overall life direction. "
        "It reflects how one approaches life and how others perceive them. Influences on this house shape "
        "confidence, vitality, behavior, and the individual's fundamental outlook toward experiences and challenges."
    ),
    2: (
        "The 2nd house governs wealth, speech, family values, and material resources. It reflects how one "
        "earns, saves, and manages financial stability, as well as the manner of communication and attachment "
        "to possessions and security."
    ),
    3: (
        "The 3rd house signifies courage, initiative, communication, and personal effort. It reflects "
        "determination, skill development, and the willingness to take action. It also governs relationships "
        "with siblings and the ability to pursue goals with persistence."
    ),
    4: (
        "The 4th house represents home, emotional well-being, inner peace, and foundational security. "
        "It reflects one's connection to family, comfort, and sense of belonging, as well as mental peace "
        "and contentment."
    ),
    5: (
        "The 5th house governs creativity, intellect, learning, and self-expression. It reflects one's "
        "ability to think, create, and express individuality. It is also associated with joy, inspiration, "
        "and the pursuit of knowledge and meaningful experiences."
    ),
    6: (
        "The 6th house represents challenges, discipline, health, and service. It reflects one's ability "
        "to handle obstacles, maintain routine, and grow through effort. This house also governs work ethic, "
        "responsibilities, and the ability to overcome difficulties."
    ),
    7: (
        "The 7th house governs partnerships, relationships, and interactions with others. It reflects how "
        "one connects, cooperates, and forms meaningful bonds, including marriage and professional partnerships."
    ),
    8: (
        "The 8th house represents transformation, hidden aspects of life, and deep inner change. It reflects "
        "one's ability to navigate uncertainty, explore deeper truths, and undergo personal evolution through "
        "life's intense experiences."
    ),
    9: (
        "The 9th house governs higher knowledge, wisdom, spirituality, and life philosophy. It reflects "
        "one's belief systems, guidance, and connection to purpose, as well as opportunities for growth "
        "through learning and exploration."
    ),
    10: (
        "The 10th house represents career, achievements, reputation, and public life. It reflects one's "
        "ambitions, responsibilities, and the role they play in society, shaping professional success "
        "and recognition."
    ),
    11: (
        "The 11th house governs gains, aspirations, and social connections. It reflects fulfillment of "
        "desires, achievements through networks, and the ability to realize long-term goals."
    ),
    12: (
        "The 12th house represents the inner world, detachment, and spiritual growth. It reflects "
        "introspection, release, and the ability to move beyond material attachments toward deeper "
        "understanding and peace."
    ),
}

PLANET_MEANINGS = {
    "Sun": "soul, authority, father, confidence, government, leadership and vitality",
    "Moon": "mind, emotions, mother, comfort, public connection and mental peace",
    "Mars": "energy, courage, land, siblings, conflict, engineering and action",
    "Mercury": "intellect, speech, business, communication, learning, logic and technology",
    "Jupiter": "wisdom, dharma, children, teacher, prosperity, guidance and expansion",
    "Venus": "love, marriage, beauty, luxury, arts, comforts, vehicles and pleasure",
    "Saturn": "karma, discipline, delay, responsibility, hard work, maturity and endurance",
    "Rahu": "ambition, foreign influence, technology, obsession, sudden rise and illusion",
    "Ketu": "detachment, spirituality, moksha, isolation, past karma and inner liberation",
    "Lagna": "the self, body, identity, personality and life direction",
}

PLANET_IN_HOUSE = {
    "Sun": {
        1:  "Sun in the 1st house gives a commanding, self-assured personality. The individual naturally takes a leadership role and projects confidence and authority. There is a strong drive for recognition, though pride or dominance may need to be tempered.",
        2:  "Sun in the 2nd house places emphasis on wealth, family status, and the power of speech. Financial matters are tied to self-worth and authority. The individual may hold strong views about money and family values.",
        3:  "Sun in the 3rd house empowers courage, communication, and individual effort. The individual is bold in expression and willing to assert themselves in pursuit of goals. Relationships with siblings may carry themes of pride or competition.",
        4:  "Sun in the 4th house focuses light on home, mother, and inner security. There may be a dominant or authoritative influence in the domestic sphere. Property and real estate matters can be prominent, often tied to the father or authority figures.",
        5:  "Sun in the 5th house ignites creative intelligence, confidence in self-expression, and a love of leadership. Education, speculation, and children are areas of pride. Connections with authority and government may open through these domains.",
        6:  "Sun in the 6th house gives strength to overcome illness, enemies, and competition. The individual excels in service-oriented or disciplined environments and has the capacity to defeat opposition through willpower and persistence.",
        7:  "Sun in the 7th house brings themes of authority into partnerships. The spouse or partner may be confident, independent, or in a position of status. Relationships with influential individuals are common, though ego dynamics may require balance.",
        8:  "Sun in the 8th house illuminates hidden matters — inheritance, longevity, and transformation. There is an interest in the occult, research, or matters of depth. The individual may undergo significant inner shifts through life's intense experiences.",
        9:  "Sun in the 9th house is a powerful placement for dharma, higher wisdom, and fortune. The individual has a deep sense of righteousness, a strong connection to the father or guru, and is drawn to philosophy, spirituality, and long-distance learning.",
        10: "Sun in the 10th house is one of the most auspicious career placements in Vedic astrology. It brings recognition, authority, and professional prominence. Leadership roles, government connections, or public life are natural expressions of this placement.",
        11: "Sun in the 11th house supports gains through authority, networks, and ambition. The individual achieves goals through confidence and social influence. Elder siblings or father figures may play a role in financial gains.",
        12: "Sun in the 12th house turns energy inward toward spirituality, foreign connections, and retreat. There may be expenses related to the self or a tendency toward solitude. Spiritual or charitable service can be a meaningful path.",
    },
    "Moon": {
        1:  "Moon in the 1st house gives a sensitive, intuitive, and emotionally expressive personality. The individual is naturally empathetic, with a nurturing presence and a strong connection to public life. Moods may fluctuate with circumstances.",
        2:  "Moon in the 2nd house creates emotional attachment to family, food, and financial security. Speech is gentle and nurturing. Income may fluctuate, and the individual tends to find comfort in accumulating resources for security.",
        3:  "Moon in the 3rd house makes the individual emotionally invested in communication, short travel, and relationships with siblings. Writing, storytelling, or nurturing communication may be natural strengths.",
        4:  "Moon in the 4th house is a highly favourable placement. The individual finds deep emotional contentment at home and has a strong bond with the mother. There is a natural love of comfort, peace, and domestic stability.",
        5:  "Moon in the 5th house brings emotional creativity, a love for children, and intuitive intelligence. The individual may be emotionally expressive in creative or educational pursuits. Romantic feelings are deep and sincere.",
        6:  "Moon in the 6th house can bring fluctuating health or emotional sensitivity to the demands of service. The individual may be caring toward those in need but must guard against emotional exhaustion from daily responsibilities.",
        7:  "Moon in the 7th house inclines toward emotional partnerships and a nurturing spouse. Relationships are emotionally fulfilling but may be subject to fluctuation. Public dealings are influenced by empathy and responsiveness.",
        8:  "Moon in the 8th house deepens emotional sensitivity and intuition toward hidden or transformative matters. The individual may have psychic tendencies, strong interest in the occult, or emotional experiences tied to sudden change.",
        9:  "Moon in the 9th house gives a deeply devotional and spiritually inclined nature. Fortune comes through intuition and faith. The mother may be a source of dharmic guidance. Travel, pilgrimage, and higher learning hold emotional significance.",
        10: "Moon in the 10th house brings emotional investment in career and public recognition. The individual may work in fields connected to the public, women, or emotional well-being. Career may fluctuate but public appeal is natural.",
        11: "Moon in the 11th house supports gains through social connections, emotional intelligence, and nurturing networks. Friendships are meaningful, and the individual tends to attract support through empathy and openness.",
        12: "Moon in the 12th house inclines toward introspection, spiritual retreat, and emotional sensitivity in solitude. Dreams may be vivid. Foreign lands or isolated environments may hold emotional resonance.",
    },
    "Mars": {
        1:  "Mars in the 1st house gives a bold, energetic, and action-oriented personality. The individual is driven, competitive, and quick to assert themselves. Physical vitality is strong, though impulsiveness or aggression may need conscious direction.",
        2:  "Mars in the 2nd house gives direct and forceful speech. The individual pursues wealth through effort and may accumulate through competitive fields. There can be impulsiveness with finances or conflicts within the family sphere.",
        3:  "Mars in the 3rd house is a highly empowering placement for courage, initiative, and communication. The individual is self-driven, skilled in effort, and willing to take calculated risks. Leadership among siblings is common.",
        4:  "Mars in the 4th house can bring energy, drive, or conflict into the domestic sphere. Property matters are prominent and often pursued actively. There may be tensions with the mother or in the home environment, requiring patience.",
        5:  "Mars in the 5th house generates dynamic intelligence, competitive spirit, and passion for creative expression. The individual is driven in education, sports, or creative pursuits. Relationships may be intense and emotionally charged.",
        6:  "Mars in the 6th house is considered an excellent placement. The individual has exceptional capacity to overcome enemies, illness, and obstacles. Discipline, competitive drive, and service are natural strengths.",
        7:  "Mars in the 7th house brings intensity into partnerships. Relationships are passionate and driven, but conflicts or power dynamics may arise. A strong, independent spouse is indicated. Business partnerships require clear agreements.",
        8:  "Mars in the 8th house gives endurance, willpower through transformation, and a fearless approach to life's hidden dimensions. The individual may be drawn to research, occult sciences, or fields involving risk and resilience.",
        9:  "Mars in the 9th house creates a forceful and courageous dharmic path. The individual is assertive in beliefs and may seek adventure, long-distance travel, or bold philosophical pursuits. The father may be active or assertive.",
        10: "Mars in the 10th house is a powerful career placement, supporting action, initiative, and professional drive. Technical, military, engineering, or administrative fields are natural arenas for success and recognition.",
        11: "Mars in the 11th house channels competitive energy into achieving gains and ambitions. The individual works hard to fulfill desires and build networks. Income may come through competitive or technically demanding fields.",
        12: "Mars in the 12th house directs energy toward foreign lands, spiritual effort, or behind-the-scenes activities. Courage may be expressed inwardly. Physical energy benefits from disciplined spiritual or charitable practice.",
    },
    "Mercury": {
        1:  "Mercury in the 1st house gives an analytical, communicative, and intellectually expressive personality. The individual is quick-thinking, articulate, and youthful in manner. A natural inclination toward learning, writing, or logical reasoning is evident.",
        2:  "Mercury in the 2nd house blesses the individual with skilled speech, business acumen, and the ability to accumulate wealth through intellect and trade. Communication is precise and persuasive, and there is a talent for languages or financial analysis.",
        3:  "Mercury in the 3rd house is an excellent placement for writers, communicators, and technologists. The individual is expressive, curious, and skilled at short-distance networking. Sibling relationships often involve intellectual exchange.",
        4:  "Mercury in the 4th house supports an educated domestic environment and a mentally active home life. The mother may be educated or intellectually inclined. The individual enjoys learning within familiar settings and has a quick, adaptable mind.",
        5:  "Mercury in the 5th house gives sharp intelligence, a love of education, and skill in games, writing, and creative problem-solving. The individual is intellectually playful and may enjoy mentoring or teaching others.",
        6:  "Mercury in the 6th house supports analytical roles in health, law, service, or problem-solving. The individual overcomes obstacles through logic and communication. There may be skill in identifying inefficiencies or resolving disputes.",
        7:  "Mercury in the 7th house brings intellectual compatibility into partnerships. The spouse is likely communicative, educated, or business-minded. Negotiations, agreements, and intellectual collaboration define relationship dynamics.",
        8:  "Mercury in the 8th house is inclined toward research, investigation, and the analytical exploration of hidden matters. Interest in psychology, occult sciences, or deep study is common. Communication about sensitive topics is approached carefully.",
        9:  "Mercury in the 9th house cultivates a philosophical intellect and a love of higher learning. The individual is drawn to teaching, travel, or the study of diverse belief systems. Writing on dharmic or philosophical themes may be fulfilling.",
        10: "Mercury in the 10th house supports careers in communication, business, writing, technology, or advisory roles. The individual is professionally articulate and may rise through intellectual contribution and skill in networking.",
        11: "Mercury in the 11th house supports gains through intellect, business networks, and skillful communication. The individual builds meaningful connections through wit and knowledge, often benefiting from trade or advisory relationships.",
        12: "Mercury in the 12th house turns the mind inward toward contemplation, spiritual study, or foreign intellectual pursuits. There may be an interest in languages, esoteric subjects, or work conducted behind the scenes.",
    },
    "Jupiter": {
        1:  "Jupiter in the 1st house is a highly auspicious placement, blessing the individual with wisdom, optimism, and a generous nature. There is a natural teaching quality and a broad life perspective. Physical constitution tends to be robust.",
        2:  "Jupiter in the 2nd house brings blessings of wealth, eloquent speech, and a harmonious family environment. The individual tends toward abundance and may have a gift for inspiring others through words, values, and generosity.",
        3:  "Jupiter in the 3rd house expresses wisdom through communication, writing, and teaching. The individual is generous with knowledge and may uplift siblings or community through guidance. Travel for learning is common.",
        4:  "Jupiter in the 4th house blesses the home, mother, and emotional foundation. Property gains are indicated over time, and the individual finds peace and contentment in the domestic environment. Inner happiness is a natural quality.",
        5:  "Jupiter in the 5th house is an excellent placement for intelligence, children, and dharmic creativity. The individual has profound intellectual depth, a love of philosophy, and may be blessed with talented or spiritually inclined children.",
        6:  "Jupiter in the 6th house brings a compassionate approach to service, health, and overcoming challenges. The individual may face some adversaries but handles them with grace. Careers in healing, law, or social service are favoured.",
        7:  "Jupiter in the 7th house is highly favourable for marriage and partnerships. The spouse is likely wise, dharmic, and supportive. Business partnerships are grounded in trust and shared values. Relationships expand the individual's worldview.",
        8:  "Jupiter in the 8th house supports longevity, hidden wisdom, and a philosophical approach to transformation. The individual may inherit resources or gain through joint ventures. Interest in occult, metaphysics, or deep research is natural.",
        9:  "Jupiter in the 9th house is considered one of the most powerful placements in Vedic astrology. It brings strong dharma, spiritual grace, blessings from gurus, fortune, and a deep connection to higher wisdom and divine guidance.",
        10: "Jupiter in the 10th house supports a respected and dharmic career. The individual may work as a teacher, advisor, counsellor, or in a role of ethical leadership. Professional recognition comes through integrity and wisdom.",
        11: "Jupiter in the 11th house brings abundant gains, fulfillment of desires, and a wide circle of beneficial connections. The individual attracts supportive friendships and achieves ambitions through wisdom and right timing.",
        12: "Jupiter in the 12th house inclines toward spiritual depth, generosity, and connection to foreign or isolated spiritual environments. The individual may find meaning in service, retreat, or giving without expectation of return.",
    },
    "Venus": {
        1:  "Venus in the 1st house gives charm, grace, and an attractive presence. The individual has a natural love of beauty, comfort, and the arts. Social ease and a pleasant disposition make them appealing to others.",
        2:  "Venus in the 2nd house blesses with wealth, beautiful speech, and a comfortable family life. The individual may accumulate through artistic, luxury, or financial fields. Family relationships are generally harmonious and affectionate.",
        3:  "Venus in the 3rd house brings artistic flair to communication, writing, and creative expression. Relationships with siblings are warm and supportive. The individual may find joy in short travels, music, poetry, or visual arts.",
        4:  "Venus in the 4th house creates a beautiful and comfortable home environment. The individual values domestic harmony, has a loving relationship with the mother, and may enjoy vehicles, property, and material comforts.",
        5:  "Venus in the 5th house brings romantic creativity, a love of the arts, and deep affection for children. The individual expresses love through creativity and may be gifted in music, dance, or aesthetics.",
        6:  "Venus in the 6th house may bring challenges in love or comfort through service. The individual may work in health, beauty, or service industries. Relationships require balance, and self-care is important for emotional well-being.",
        7:  "Venus in the 7th house is highly auspicious for marriage. The spouse is likely attractive, refined, and loving. Partnerships are harmonious, and the individual naturally attracts supportive, affectionate companions.",
        8:  "Venus in the 8th house brings depth and intensity to love and relationships. There is attraction to hidden beauty, transformative experiences, and mystical or artistic expression. Shared resources and inheritances may be prominent.",
        9:  "Venus in the 9th house combines love with dharma, bringing devotion, artistic or spiritual refinement, and fortune through relationships. The individual may be drawn to the arts of different cultures or spiritual traditions.",
        10: "Venus in the 10th house supports careers in arts, beauty, entertainment, luxury, or diplomacy. The individual projects charm and refinement professionally and may gain recognition through creative or relational skills.",
        11: "Venus in the 11th house brings social popularity, gains through relationships and creative pursuits, and fulfillment in artistic or recreational networks. Friendships are warm, and desires are gradually fulfilled.",
        12: "Venus in the 12th house inclines toward spiritual love, surrender, and pleasures experienced in solitude or foreign environments. There may be a fondness for retreats, distant places, or devotional artistic practices.",
    },
    "Saturn": {
        1:  "Saturn in the 1st house gives a serious, reserved, and disciplined personality. Life lessons often begin early, building resilience and depth over time. The individual grows steadily in wisdom and earns respect through perseverance.",
        2:  "Saturn in the 2nd house introduces karmic lessons around wealth, speech, and family. Financial growth may be delayed but becomes stable with patience and discipline. Speech tends to be measured, and family responsibilities may be significant.",
        3:  "Saturn in the 3rd house rewards consistent effort, persistence, and disciplined communication. Progress through self-initiative may be slow but steady. Relationships with siblings may carry karmic themes or require patience.",
        4:  "Saturn in the 4th house can delay domestic happiness or create karmic responsibilities at home. The mother may represent discipline or duty. Property and real estate matters develop with time and effort, eventually bringing stability.",
        5:  "Saturn in the 5th house brings a disciplined approach to education, creativity, and children. Intelligence is methodical and thorough. Children may come later in life. Learning is taken seriously, and creative work requires sustained effort.",
        6:  "Saturn in the 6th house is an excellent placement for overcoming obstacles through sustained effort. The individual is highly disciplined in service, excels in long-term health routines, and defeats enemies through patience and endurance.",
        7:  "Saturn in the 7th house often indicates a serious or delayed marriage. The spouse may be older, disciplined, or carry karmic significance. Partnerships are built on duty and commitment rather than passion, strengthening over time.",
        8:  "Saturn in the 8th house supports long life but may bring karmic burdens related to hidden matters, inheritance, or transformation. The individual handles deep change with stoicism and gradually develops inner resilience.",
        9:  "Saturn in the 9th house creates a disciplined, earnest approach to dharma and higher knowledge. Karmic lessons may come through the father or guru. The individual earns spiritual and philosophical understanding through sincere effort.",
        10: "Saturn in the 10th house is one of the strongest career placements. The rise may be slow and demanding, but the individual builds lasting authority, recognition, and professional mastery through dedicated effort over time.",
        11: "Saturn in the 11th house brings disciplined ambitions and delayed but substantial gains. The individual builds networks through reliability and sustained effort. Friendships are few but deep, and long-term goals are eventually realised.",
        12: "Saturn in the 12th house supports deep spiritual discipline, service in isolation, and karmic detachment from material outcomes. Foreign experiences, retreat, or humanitarian service may be areas of karmic fulfillment.",
    },
    "Rahu": {
        1:  "Rahu in the 1st house creates an intense, magnetic, and unconventional personality. The individual is driven by a powerful desire for self-expression and recognition. Identity may go through significant transformation across life, and there is a natural pull toward paths that break from tradition.",
        2:  "Rahu in the 2nd house intensifies the desire for wealth, status, and material accumulation. Speech may be persuasive or unconventional. Financial gains can be sudden or come from unusual or foreign sources. Family background may be diverse or atypical.",
        3:  "Rahu in the 3rd house amplifies ambition, courage, and the drive for self-promotion. The individual may be exceptionally bold in communication, entrepreneurship, or media. There is a strong desire to distinguish oneself through effort, skill, and initiative.",
        4:  "Rahu in the 4th house creates restlessness in the domestic sphere. There may be an intense desire for property, comfort, or a sense of belonging that remains elusive. Foreign environments or unconventional living situations may feature prominently.",
        5:  "Rahu in the 5th house brings an unconventional and intensely curious intelligence. Creative pursuits may be unusual or ahead of their time. There is fascination with speculation, romance, or self-expression, though outcomes may be unpredictable.",
        6:  "Rahu in the 6th house is a powerful placement for overcoming enemies, competition, and obstacles through unconventional or foreign means. The individual may excel in technical, scientific, or service-related fields and shows great tenacity in challenging situations.",
        7:  "Rahu in the 7th house creates intense, karmically significant partnerships. The spouse or partner may be from a different background or culture. Relationships may be transformative but also unpredictable, requiring conscious attention to boundaries and expectations.",
        8:  "Rahu in the 8th house generates a deep fascination with occult sciences, hidden knowledge, and transformation. The individual may experience sudden and intense life changes. Research, investigation, or metaphysical pursuits may become consuming interests.",
        9:  "Rahu in the 9th house creates an unconventional approach to dharma, philosophy, and belief. The individual may question traditional teachings and seek truth through unorthodox paths. Fortune may come through foreign cultures, travel, or progressive ideologies.",
        10: "Rahu in the 10th house is associated with a strong drive for fame, status, and professional achievement. The individual may rise suddenly or through unconventional means. Careers in technology, foreign affairs, media, or mass communication may be favoured.",
        11: "Rahu in the 11th house is an excellent placement for material gains and ambitious networking. The individual attracts unusual alliances and may achieve goals through large-scale or foreign connections. Financial gains can be substantial but should be managed wisely.",
        12: "Rahu in the 12th house pulls toward foreign lands, spiritual obsession, or hidden pleasures. The individual may spend considerably on foreign travel, spiritual pursuits, or desires that operate below the surface. Vivid dreams and subconscious intensity are common.",
    },
    "Ketu": {
        1:  "Ketu in the 1st house brings a spiritually inclined, introspective personality. The individual may feel a sense of detachment from physical identity, carrying deep past-life wisdom. There is a natural disinterest in ego-driven pursuits and a pull toward inner truth.",
        2:  "Ketu in the 2nd house indicates detachment from material wealth and conventional family values. The individual may not be strongly motivated by accumulation and often speaks with directness or spiritual depth. Karmic lessons around resources and belonging are present.",
        3:  "Ketu in the 3rd house reflects past-life mastery in communication, arts, or courage. The individual may not feel driven to assert themselves but carries innate creative or communicative gifts. Sibling relationships may be spiritually significant or karmically complex.",
        4:  "Ketu in the 4th house creates emotional detachment from home and domestic comfort. The individual may feel spiritually at peace in solitude rather than family life. There are karmic themes around the mother, property, or the sense of roots and belonging.",
        5:  "Ketu in the 5th house reflects past-life intellectual or creative gifts that the individual may take for granted. There is spiritual depth in learning, but detachment from outcomes — in education, romance, or children — may be a recurring theme.",
        6:  "Ketu in the 6th house is an excellent spiritual placement for healing, service, and overcoming adversaries through detachment. The individual may possess intuitive healing ability and approaches challenges with calm disengagement rather than conflict.",
        7:  "Ketu in the 7th house creates karmically significant partnerships that often carry a past-life quality. The individual may feel spiritually disconnected in conventional relationships. The spouse may be spiritually inclined, unusual, or connected through past-life bonds.",
        8:  "Ketu in the 8th house is a deeply spiritual placement. The individual possesses strong past-life occult knowledge and a natural understanding of transformation, death, and liberation. Moksha-oriented themes run through the individual's inner life.",
        9:  "Ketu in the 9th house reflects detachment from conventional dharma and organised religion. The individual seeks truth through inner experience rather than external doctrine. Past-life wisdom from teachers or gurus is carried within, often making formal spiritual instruction feel repetitive.",
        10: "Ketu in the 10th house indicates detachment from worldly recognition and career status. The individual may achieve prominence but feel unmoved by it. Spiritual, healing, or service-oriented vocations carry karmic meaning and quiet fulfillment.",
        11: "Ketu in the 11th house brings detachment from material ambitions and social gains. The individual is not strongly driven by wealth or popularity, often finding that desires fulfil themselves without great effort. Spiritual satisfaction matters more than worldly achievement.",
        12: "Ketu in the 12th house is one of the most spiritually powerful placements. There is a strong inclination toward moksha, inner liberation, and withdrawal from material life. Solitude, meditation, and surrender come naturally, carrying deep karmic resonance from past lives.",
    },
}

DASHA_GENERAL = {
    "Sun": (
        "Sun Mahadasha may bring focus on authority, career visibility, father, "
        "confidence, leadership and self-expression. It can create recognition when "
        "well placed, but ego conflicts or pressure from authority may arise when afflicted."
    ),
    "Moon": (
        "Moon Mahadasha may emphasize emotions, family, mother, home, public image, "
        "mental peace and social connection. It can bring nurturing experiences, but "
        "also emotional sensitivity and mood fluctuations."
    ),
    "Mars": (
        "Mars Mahadasha may bring action, courage, property matters, competition, "
        "technical work, conflicts and ambition. It supports initiative, but requires "
        "control over anger and impulsive decisions."
    ),
    "Mercury": (
        "Mercury Mahadasha may bring education, communication, business, technology, "
        "writing, analysis and networking. It is generally good for learning and trade, "
        "but may create overthinking when disturbed."
    ),
    "Jupiter": (
        "Jupiter Mahadasha may bring wisdom, dharma, children, teaching, prosperity, "
        "guidance, spiritual learning and expansion. It often supports growth, ethics "
        "and blessings when Jupiter is strong."
    ),
    "Venus": (
        "Venus Mahadasha may bring relationships, marriage, comforts, luxury, creativity, "
        "vehicles, artistic growth and material enjoyment. It can be pleasant, but excess "
        "attachment to pleasure should be balanced."
    ),
    "Saturn": (
        "Saturn Mahadasha may bring discipline, responsibility, career maturity, delays, "
        "karma, endurance and long-term stability. It can feel heavy, but often builds "
        "lasting success through patience and hard work."
    ),
    "Rahu": (
        "Rahu Mahadasha may bring ambition, foreign connections, technology, unusual rise, "
        "experimentation and worldly desire. It can give sudden growth, but also confusion, "
        "restlessness or unconventional situations."
    ),
    "Ketu": (
        "Ketu Mahadasha may bring detachment, spirituality, isolation, inner search, "
        "past-life karma and liberation themes. It may reduce worldly attachment and push "
        "the individual toward deeper self-understanding."
    ),
}


def get_chart(result, chart_key="d1_rashi_chart"):
    return result.get(chart_key, {})


def planet_line(planet, pos):
    retro = " retrograde" if pos.get("retrograde") and planet not in ["Rahu", "Ketu", "Lagna"] else ""
    return (
        f"{planet} is placed in {pos['rashi']} at {pos['degree_in_rashi']:.2f}° "
        f"in house {pos['house']}, in {pos['nakshatra']} nakshatra pada {pos['pada']}{retro}."
    )


def interpret_lagna(result):
    d1 = get_chart(result)
    lagna = d1["Lagna"]
    rashi = lagna["rashi"]

    paragraphs = [
        (
            f"Lagna falls at {lagna['degree_in_rashi']:.2f}° in {rashi}, in "
            f"{lagna['nakshatra']} nakshatra pada {lagna['pada']}. This point represents the individual's body, "
            f"temperament, identity, health tendency and life direction."
        ),
        RASHI_DESCRIPTION.get(rashi, f"The Lagna is in {rashi}, shaping the individual's core personality and approach to life."),
    ]

    planets_in_first = [
        p for p, pos in d1.items()
        if pos["house"] == 1 and p != "Lagna"
    ]

    if planets_in_first:
        paragraphs.append(
            "Planets placed in the 1st house strongly influence personality. "
            f"In this chart, the 1st house contains: {', '.join(planets_in_first)}."
        )

    return {
        "title": "Lagna and Personality Analysis",
        "paragraphs": paragraphs,
    }


def interpret_houses(result):
    d1 = get_chart(result)
    sections = []

    for house in range(1, 13):
        planets = [
            p for p, pos in d1.items()
            if pos["house"] == house and p != "Lagna"
        ]

        if house == 1:
            lagna_pos = d1["Lagna"]
            if planets:
                planet_list = ", ".join(planets)
                paragraphs = [
                    HOUSE_INTRO[1],
                    f"This house is anchored by the Ascendant (Lagna) in {lagna_pos['rashi']}, "
                    f"and is further influenced by the presence of {planet_list}. "
                    "Together, these energies shape the individual's outward personality, physical constitution, and life approach.",
                ]
            else:
                paragraphs = [
                    HOUSE_INTRO[1],
                    f"This house is anchored by the Ascendant (Lagna) in {lagna_pos['rashi']}. "
                    "No additional planets are directly placed here, so the expression of self is shaped "
                    "primarily by the Lagna sign, its lord, and active dasha periods.",
                ]
            for planet in planets:
                house_specific = PLANET_IN_HOUSE.get(planet, {}).get(1)
                if house_specific:
                    paragraphs.append(house_specific)
                else:
                    meaning = PLANET_MEANINGS.get(planet, "")
                    paragraphs.append(
                        f"{planet} represents {meaning}. Its placement in the 1st house directly "
                        f"colours the individual's personality, appearance, and self-expression."
                    )
        else:
            paragraphs = [HOUSE_INTRO[house]]
            if planets:
                paragraphs.append(
                    f"Planets influencing this house by placement: {', '.join(planets)}."
                )
                for planet in planets:
                    house_specific = PLANET_IN_HOUSE.get(planet, {}).get(house)
                    if house_specific:
                        paragraphs.append(house_specific)
                    else:
                        meaning = PLANET_MEANINGS.get(planet, "")
                        paragraphs.append(
                            f"{planet} represents {meaning}. Since it is placed in the {house} house, "
                            f"its energy becomes connected with {HOUSE_MEANINGS[house]}."
                        )
            else:
                paragraphs.append(
                    "No major planet is directly placed in this house. Results will depend on the house lord, aspects and dasha periods."
                )

        sections.append({
            "title": f"Bhava {house} Interpretation",
            "paragraphs": paragraphs,
        })

    return sections


def interpret_planets(result):
    d1 = get_chart(result)
    sections = []

    order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    for planet in order:
        pos = d1[planet]
        house_specific = PLANET_IN_HOUSE.get(planet, {}).get(pos["house"])
        paragraphs = [
            planet_line(planet, pos),
            f"{planet} signifies {PLANET_MEANINGS.get(planet)}.",
            RASHI_DESCRIPTION.get(pos['rashi'], f"The sign {pos['rashi']} adds a unique quality to {planet}'s expression."),
            (
                f"{planet}'s significations are expressed through {pos['rashi']}'s "
                f"{RASHI_NATURE.get(pos['rashi'], 'distinctive')} quality, shaping the way "
                f"its energy manifests in this placement."
            ),
        ]
        if house_specific:
            paragraphs.append(house_specific)

        if pos.get("retrograde") and planet not in ["Rahu", "Ketu"]:
            paragraphs.append(
                f"{planet} is retrograde, which may internalize its energy and make its results more karmic, delayed or reflective."
            )

        sections.append({
            "title": f"{planet} Interpretation",
            "paragraphs": paragraphs,
        })

    return sections


def find_conjunctions(result):
    d1 = get_chart(result)
    house_map = {}

    for planet, pos in d1.items():
        house_map.setdefault(pos["house"], []).append(planet)

    paragraphs = []

    for house, planets in sorted(house_map.items()):
        if len(planets) > 1:
            paragraphs.append(
                f"House {house} contains a conjunction or combined influence of: {', '.join(planets)}. "
                f"This intensifies matters of {HOUSE_MEANINGS.get(house)}."
            )

            for i in range(len(planets)):
                for j in range(i + 1, len(planets)):
                    p1, p2 = planets[i], planets[j]
                    deg1 = d1[p1]["degree_in_rashi"]
                    deg2 = d1[p2]["degree_in_rashi"]
                    diff = abs(deg1 - deg2)
                    strength = "very strong" if diff <= 5 else "strong" if diff <= 10 else "moderate" if diff <= 15 else "mild"
                    paragraphs.append(
                        f"{p1} and {p2} are about {diff:.2f}° apart in the same house/sign, giving a {strength} conjunction effect."
                    )

    if not paragraphs:
        paragraphs.append("No major same-house conjunctions are present among the primary planets.")

    return {
        "title": "Conjunction Analysis",
        "paragraphs": paragraphs,
    }


def find_special_aspects(result):
    d1 = get_chart(result)
    paragraphs = [
        "In Vedic astrology, drishti (aspect) represents the directional influence of a planet. "
        "A planet not only impacts the house it occupies, but also projects its energy onto specific "
        "houses through aspects.",
        "These aspects modify the results of the aspected house by introducing the nature of the "
        "influencing planet — whether it brings growth, discipline, intensity, confusion or detachment.",
        "Understanding drishti helps reveal hidden connections between different areas of life and "
        "shows how one domain influences another.",
        "General Drishti Rules: Every planet aspects the 7th house from its position (full opposite aspect). "
        "In addition, Mars casts special aspects on the 4th and 8th houses from its placement. "
        "Jupiter aspects the 5th and 9th houses from its placement. "
        "Saturn aspects the 3rd and 10th houses from its placement. "
        "Rahu and Ketu, like Jupiter, aspect the 5th and 9th houses from their placement. "
        "Sun, Moon, Mercury and Venus cast only the standard 7th house aspect.",
    ]

    aspect_rules = {
        "Sun":     [7],
        "Moon":    [7],
        "Mercury": [7],
        "Venus":   [7],
        "Mars":    [4, 7, 8],
        "Jupiter": [5, 7, 9],
        "Saturn":  [3, 7, 10],
        "Rahu":    [5, 7, 9],
        "Ketu":    [5, 7, 9],
    }

    for planet, aspects in aspect_rules.items():
        if planet not in d1:
            continue

        from_house = d1[planet]["house"]

        for aspect in aspects:
            target_house = ((from_house + aspect - 2) % 12) + 1
            paragraphs.append(
                f"{planet} from house {from_house} aspects house {target_house}. "
                f"This influences matters of {HOUSE_MEANINGS.get(target_house)}."
            )

    return {
        "title": "Drishti / Aspect Analysis",
        "paragraphs": paragraphs,
    }


D9_PLANET_THEMES = {
    "Sun":     "inner authority, soul purpose, and dharmic identity",
    "Moon":    "emotional maturity, inner peace, and relational sensitivity",
    "Mars":    "inner drive, courage in commitments, and deeper willpower",
    "Mercury": "communication in relationships, adaptability, and inner intellect",
    "Jupiter": "wisdom, dharmic expansion, and blessings in marriage and spiritual growth",
    "Venus":   "relationship harmony, marriage potential, and inner values",
    "Saturn":  "karmic discipline, long-term commitment, and inner resilience",
    "Rahu":    "deeper ambitions, karmic desires, and unconventional inner growth",
    "Ketu":    "past-life wisdom, spiritual detachment, and inner liberation",
}

def interpret_d9(result):
    d9 = get_chart(result, "d9_navamsa_chart")
    d1 = get_chart(result, "d1_rashi_chart")

    paragraphs = [
        "The D9 Navamsa chart reveals the deeper dimensions of the birth chart — dharma, inner maturity, "
        "marriage potential, and the true strength of each planet as it matures over time.",
        "A planet placed in the same sign in both D1 and D9 is called Vargottama, a classical indicator "
        "of heightened strength and clarity of expression across the lifetime.",
    ]

    # Lagna
    lagna_d9 = d9.get("Lagna")
    lagna_d1 = d1.get("Lagna")
    if lagna_d9:
        varg = " This Lagna is Vargottama, indicating a strong and consistent sense of self." \
            if lagna_d9["rashi"] == lagna_d1["rashi"] else ""
        paragraphs.append(
            f"The D9 Ascendant falls in {lagna_d9['rashi']} (house {lagna_d9['house']}), "
            f"shaping the individual's inner character, dharmic inclination, and approach to relationships.{varg}"
        )

    # All 9 planets
    planet_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    for planet in planet_order:
        pos9 = d9.get(planet)
        pos1 = d1.get(planet)
        if not pos9:
            continue
        theme = D9_PLANET_THEMES.get(planet, "inner expression")
        nature = RASHI_NATURE.get(pos9["rashi"], "distinctive")
        varg = ""
        if pos1 and pos9["rashi"] == pos1["rashi"]:
            varg = f" Being Vargottama (same sign in D1 and D9), {planet}'s influence is considered especially potent and enduring."
        retro = ""
        if pos9.get("retrograde") and planet not in ("Rahu", "Ketu"):
            retro = " Its retrograde state in D9 suggests a more internalised and reflective expression of these themes."
        paragraphs.append(
            f"{planet} in D9 is placed in {pos9['rashi']} (house {pos9['house']}), "
            f"in {pos9['nakshatra']} nakshatra pada {pos9['pada']}. "
            f"This {nature} placement deepens the individual's {theme}.{varg}{retro}"
        )

    return {
        "title": "D9 Navamsa Interpretation",
        "paragraphs": paragraphs,
    }


def interpret_mahadashas(result):
    d1 = get_chart(result)
    dashas = result.get("vimshottari_mahadasha", [])
    paragraphs = []

    for dasha in dashas:
        lord = dasha["lord"]
        pos = d1.get(lord)

        text = (
            f"{lord} Mahadasha runs from {dasha['start']} to {dasha['end']} "
            f"for approximately {dasha['years']} years. {DASHA_GENERAL.get(lord, '')}"
        )

        if pos:
            text += (
                f" In this chart, {lord} is placed in {pos['rashi']} in house {pos['house']}, "
                f"in {pos['nakshatra']} nakshatra pada {pos['pada']}. Therefore this period may strongly activate "
                f"{HOUSE_MEANINGS.get(pos['house'])}."
            )

        paragraphs.append(text)

    return {
        "title": "Vimshottari Mahadasha Life Themes",
        "paragraphs": paragraphs,
    }


CAREER_PLANET_THEMES = {
    "Sun":     "leadership, government roles, administration, and positions of authority",
    "Moon":    "public-facing roles, hospitality, caregiving, and fields connected to the masses",
    "Mars":    "engineering, military, sports, surgery, real estate, and competitive fields",
    "Mercury": "communication, business, writing, technology, teaching, and analytical work",
    "Jupiter": "education, law, consulting, finance, counselling, and advisory roles",
    "Venus":   "arts, beauty, luxury, entertainment, diplomacy, and creative industries",
    "Saturn":  "structured professions, service sectors, law, discipline-based fields, and long-term careers",
    "Rahu":    "foreign industries, technology, media, unconventional careers, and mass-scale pursuits",
    "Ketu":    "research, healing, spiritual vocations, and behind-the-scenes technical work",
    "Lagna":   "a strong personal drive that shapes professional direction",
}

HOUSE_CAREER_ROLE = {
    2:  "supporting income, financial stability, and the accumulation of professional resources",
    6:  "bringing discipline, competition, and the ability to overcome workplace challenges",
    10: "directly shaping career, public status, authority, and professional recognition",
    11: "generating gains, income, and the fulfillment of professional ambitions",
}

SPIRITUAL_HOUSE_THEMES = {
    5:  "the 5th house of mantra, purva punya (past-life merit), and devotional creativity",
    8:  "the 8th house of occult sciences, hidden wisdom, and inner transformation",
    9:  "the 9th house of dharma, higher knowledge, guru blessings, and spiritual fortune",
    12: "the 12th house of moksha, surrender, retreat, and liberation from material attachment",
}

SPIRITUAL_PLANET_THEMES = {
    "Sun":     "the soul's search for higher purpose, dharmic identity, and connection to divine light",
    "Moon":    "emotional devotion, intuitive spiritual sensitivity, and inner peace through surrender",
    "Mars":    "courageous spiritual effort, disciplined practice, and the fire of inner transformation",
    "Mercury": "the intellectual pursuit of wisdom, study of sacred texts, and analytical spirituality",
    "Jupiter": "grace, dharmic guidance, guru blessings, and the expansion of spiritual knowledge",
    "Venus":   "devotional love, bhakti, artistic worship, and the beauty of spiritual expression",
    "Saturn":  "disciplined sadhana, karmic purification, and the patient unfolding of spiritual maturity",
    "Rahu":    "unconventional spiritual seeking, deep questioning of tradition, and karmic spiritual intensity",
    "Ketu":    "natural spiritual detachment, past-life wisdom, and a strong inclination toward inner liberation",
}


def interpret_career(result):
    d1 = get_chart(result)

    paragraphs = [
        "In Vedic astrology, career is primarily studied through the 10th house of profession and public life, "
        "supported by the 2nd house of income and accumulated resources, the 6th house of service and discipline, "
        "and the 11th house of gains and the fulfillment of ambitions.",
    ]

    tenth_planets = [p for p, pos in d1.items() if pos["house"] == 10 and p != "Lagna"]
    if tenth_planets:
        paragraphs.append(
            f"The 10th house — the primary house of career — contains: {', '.join(tenth_planets)}. "
            "This gives a strong direct influence on professional identity and public recognition."
        )
        for planet in tenth_planets:
            pos = d1[planet]
            theme = CAREER_PLANET_THEMES.get(planet, "a unique professional influence")
            paragraphs.append(
                f"{planet} in the 10th house indicates a natural affinity toward {theme}. "
                f"Placed in {pos['rashi']}, it colours professional expression with a "
                f"{RASHI_NATURE.get(pos['rashi'], 'distinctive')} quality."
            )
    else:
        paragraphs.append(
            "No major planet is directly placed in the 10th house. Career direction will be shaped "
            "primarily by the 10th lord's placement, active dasha periods, and supporting career houses."
        )

    other_career = [(p, pos) for p, pos in d1.items() if pos["house"] in [2, 6, 11] and p != "Lagna"]
    if other_career:
        paragraphs.append("Additional planetary influences on career and income:")
        for planet, pos in other_career:
            theme = CAREER_PLANET_THEMES.get(planet, "a professional influence")
            role = HOUSE_CAREER_ROLE.get(pos["house"], "influencing career matters")
            paragraphs.append(
                f"{planet} in house {pos['house']} ({pos['rashi']}) contributes by {role}. "
                f"Its significations of {theme} become active in this domain."
            )

    return {
        "title": "Career and Work Direction",
        "paragraphs": paragraphs,
    }


def interpret_relationships(result):
    d1 = get_chart(result)
    d9 = get_chart(result, "d9_navamsa_chart")

    paragraphs = [
        "In Vedic astrology, marriage and relationships are studied through the 7th house of partnerships, "
        "Venus as the natural significator of love and harmony, Jupiter as the significator of the spouse "
        "(especially significant for women), and the D9 Navamsa chart which reveals the deeper dimensions "
        "of relationship potential and inner compatibility.",
    ]

    seventh_planets = [p for p, pos in d1.items() if pos["house"] == 7]
    if seventh_planets:
        paragraphs.append(
            f"The 7th house contains: {', '.join(seventh_planets)}. "
            "Planets placed here directly colour the nature of partnerships, the qualities of the spouse, "
            "and the overall dynamic of committed relationships."
        )
        for planet in seventh_planets:
            pos = d1[planet]
            house_specific = PLANET_IN_HOUSE.get(planet, {}).get(7)
            if house_specific:
                paragraphs.append(house_specific)
            else:
                paragraphs.append(
                    f"{planet} in the 7th house brings its significations of {PLANET_MEANINGS.get(planet, '')} "
                    f"into the domain of partnerships and marriage."
                )
    else:
        paragraphs.append(
            "The 7th house has no major planet directly placed in it. Relationship themes will be shaped "
            "by the 7th lord's placement, Venus, Jupiter, and the timing of relevant dasha periods."
        )

    if "Venus" in d1:
        v = d1["Venus"]
        paragraphs.append(
            f"Venus — the natural karaka of love, beauty, and harmony — is placed in {v['rashi']} "
            f"in house {v['house']}. This shapes the individual's relationship style, sense of attraction, "
            f"and the qualities they seek in a partner. The {RASHI_NATURE.get(v['rashi'], 'distinctive')} "
            f"nature of {v['rashi']} colours how Venus expresses love and partnership in this chart."
        )

    if "Jupiter" in d1:
        ju = d1["Jupiter"]
        paragraphs.append(
            f"Jupiter — the significator of the spouse, wisdom, and dharmic bonds — is placed in "
            f"{ju['rashi']} in house {ju['house']}. Jupiter's strength and placement influence the "
            f"quality of marital blessings, the character of the spouse, and the dharmic foundation "
            f"of long-term partnerships."
        )

    if "Venus" in d9:
        v9 = d9["Venus"]
        paragraphs.append(
            f"In the D9 Navamsa chart, Venus falls in {v9['rashi']} (house {v9['house']}). "
            f"This reveals the deeper maturity of relationship energy — the inner values, emotional "
            f"readiness, and karmic themes that emerge within committed partnerships over time."
        )

    if "Jupiter" in d9:
        ju9 = d9["Jupiter"]
        paragraphs.append(
            f"In D9, Jupiter falls in {ju9['rashi']} (house {ju9['house']}), reflecting the dharmic "
            f"quality of the marital bond and the depth of wisdom and grace that the individual brings "
            f"to their closest relationships."
        )

    return {
        "title": "Marriage and Relationship Indications",
        "paragraphs": paragraphs,
    }


def interpret_spirituality(result):
    d1 = get_chart(result)

    paragraphs = [
        "Spiritual tendencies in a chart are revealed through the 5th house of mantra and past-life merit, "
        "the 8th house of occult depth and inner transformation, the 9th house of dharma and higher wisdom, "
        "and the 12th house of moksha and spiritual surrender. Jupiter and Ketu are the primary natural "
        "significators of spiritual growth and inner liberation.",
    ]

    seen = set()
    spiritual_planets = []
    for planet, pos in d1.items():
        if planet in seen:
            continue
        if pos["house"] in [5, 8, 9, 12] or planet in ["Jupiter", "Ketu"]:
            spiritual_planets.append((planet, pos))
            seen.add(planet)

    if not spiritual_planets:
        paragraphs.append(
            "No major planets are directly placed in the primary spiritual houses. Spiritual inclinations "
            "will emerge more through dasha periods and the natural significations of Jupiter and Ketu."
        )
    else:
        for planet, pos in spiritual_planets:
            house = pos["house"]
            planet_theme = SPIRITUAL_PLANET_THEMES.get(planet, "a subtle spiritual quality")
            if house in SPIRITUAL_HOUSE_THEMES:
                house_context = SPIRITUAL_HOUSE_THEMES[house]
                paragraphs.append(
                    f"{planet} is placed in {house_context}. This deepens the individual's connection to "
                    f"{planet_theme}, bringing these themes into direct focus within the life journey."
                )
            else:
                paragraphs.append(
                    f"{planet} carries its spiritual significations of {planet_theme} through its natural "
                    f"role in the chart, regardless of house placement."
                )

    return {
        "title": "Spiritual and Dharma Indications",
        "paragraphs": paragraphs,
    }


def generate_interpretation_report(result):
    sections = []

    sections.append(interpret_lagna(result))
    sections.extend(interpret_houses(result))
    sections.extend(interpret_planets(result))
    sections.append(find_conjunctions(result))
    sections.append(find_special_aspects(result))
    sections.append(interpret_d9(result))
    sections.append(interpret_career(result))
    sections.append(interpret_relationships(result))
    sections.append(interpret_spirituality(result))
    sections.append(interpret_mahadashas(result))

    return sections